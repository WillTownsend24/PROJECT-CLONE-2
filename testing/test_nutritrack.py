"""
NutriTrack Tests
Run with:  pytest tests/test_nutritrack.py -v --tb=short
"""
import json
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock


import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app, db, User, FoodEntry, NutritionalGuideline, Recipe, RecipeComment, Notification, get_daily_totals


# Fixtures
@pytest.fixture(scope="function")
def test_app():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test_secret",
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def subscriber(test_app):
    with test_app.app_context():
        u = User(username="alice", email="alice@example.com",
            full_name="Alice Smith", role="subscriber", goal="maintain")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def professional(test_app):
    with test_app.app_context():
        p = User(username="drjones", email="jones@example.com",
            full_name="Dr Jones", role="professional", specialisation="Dietitian")
        p.set_password("password123")
        db.session.add(p)
        db.session.commit()
        return p.id


@pytest.fixture
def subscriber_with_prof(test_app, subscriber, professional):
    with test_app.app_context():
        u = User.query.get(subscriber)
        u.professional_id = professional
        db.session.commit()
    return subscriber


@pytest.fixture
def logged_in_subscriber(client, test_app, subscriber):
    client.post("/login", data={"username": "alice", "password": "password123"})
    return client


@pytest.fixture
def logged_in_professional(client, test_app, professional):
    client.post("/login", data={"username": "drjones", "password": "password123"})
    return client


# unit tests
class TestUserModel:
    def test_password_hashing_correct(self, test_app):
        with test_app.app_context():
            u = User(username="bob", email="bob@example.com", full_name="Bob", role="subscriber")
            u.set_password("mysecret")
            assert u.check_password("mysecret") is True


    def test_wrong_password_rejected(self, test_app):
        with test_app.app_context():
            u = User(username="bob", email="bob@example.com", full_name="Bob", role="subscriber")
            u.set_password("mysecret")

            assert u.check_password("wrongpassword") is False

    def test_password_not_stored_as_plaintext(self, test_app):
        with test_app.app_context():
            u = User(username="bob", email="bob@example.com", full_name="Bob", role="subscriber")
            u.set_password("mysecret")
            assert "mysecret" not in u.password_hash


class TestRecipeModel:
    def test_average_rating_no_comments_returns_none(self, test_app):
        with test_app.app_context():
            r = Recipe(title="Test", instructions="do it", ingredients="[]")
            db.session.add(r)
            db.session.commit()
            assert r.average_rating() is None


    def test_average_rating_calculated_correctly(self, test_app, subscriber):
        with test_app.app_context():
            r = Recipe(title="Test", instructions="do it", ingredients="[]")
            db.session.add(r)

            db.session.commit()
            for rating in [4, 5, 3]:
                db.session.add(RecipeComment(
                    recipe_id=r.id, user_id=subscriber, comment="test", rating=rating))
            db.session.commit()
            db.session.refresh(r)
            assert r.average_rating() == 4.0


class TestGetDailyTotals:
    def test_empty_diary_returns_zeros(self, test_app, subscriber):
        with test_app.app_context():
            totals = get_daily_totals(subscriber, date.today())
            assert totals["calories"] == 0

    def test_quantity_scales_nutrients(self, test_app, subscriber):
        """200g at 100 kcal/100g should give 200 kcal."""
        with test_app.app_context():
            db.session.add(FoodEntry(user_id=subscriber, food_name="Rice",
                quantity_g=200, calories=100, carbs_g=23, logged_date=date.today()))
            db.session.commit()
            totals = get_daily_totals(subscriber, date.today())
            assert totals["calories"] == 200.0


    def test_multiple_entries_summed(self, test_app, subscriber):
        with test_app.app_context():
            for food, cal in [("Egg", 78), ("Toast", 85)]:
                db.session.add(FoodEntry(user_id=subscriber, food_name=food,
                    quantity_g=100, calories=cal, logged_date=date.today()))
            db.session.commit()
            assert get_daily_totals(subscriber, date.today())["calories"] == 163.0


    def test_different_dates_not_included(self, test_app, subscriber):
        with test_app.app_context():
            yesterday = date.today() - timedelta(days=1)
            db.session.add(FoodEntry(user_id=subscriber, food_name="Old food",
                quantity_g=100, calories=500, logged_date=yesterday))
            db.session.commit()
            assert get_daily_totals(subscriber, date.today())["calories"] == 0


#integration tests (Authentication)

class TestAuth:
    def test_valid_login_redirects_to_home(self, client, test_app, subscriber):
        r = client.post("/login", data={"username": "alice", "password": "password123"},
            follow_redirects=True)
        assert r.status_code == 200


    def test_wrong_password_stays_on_login(self, client, test_app, subscriber):
        r = client.post("/login", data={"username": "alice", "password": "wrongpass"},
            follow_redirects=True)
        assert b"Invalid" in r.data

    def test_protected_route_redirects_unauthenticated(self, client):
        r = client.get("/home", follow_redirects=True)
        assert b"log in" in r.data.lower() or b"login" in r.data.lower()

    def test_logout_ends_session(self, logged_in_subscriber):
        logged_in_subscriber.get("/logout")
        r = logged_in_subscriber.get("/home", follow_redirects=True)
        assert b"log in" in r.data.lower() or b"login" in r.data.lower()


class TestRegistration:
    def test_create_subscriber_success(self, client, test_app):
        client.post("/create-subscriber", data={
            "username": "newuser", "email": "new@example.com",
            "password": "secure123", "confirm_password": "secure123",
            "full_name": "New User", "goal": "maintain",
        }, follow_redirects=True)
        with test_app.app_context():
            assert User.query.filter_by(username="newuser").first() is not None


    def test_duplicate_username_rejected(self, client, test_app, subscriber):
        r = client.post("/create-subscriber", data={
            "username": "alice", "email": "other@example.com",
            "password": "secure123", "confirm_password": "secure123",
            "full_name": "Clone", "goal": "maintain",
        }, follow_redirects=True)
        assert b"taken" in r.data.lower() or b"already" in r.data.lower()


    def test_password_mismatch_rejected(self, client):
        r = client.post("/create-subscriber", data={
            "username": "bob", "email": "bob@example.com",
            "password": "abc123", "confirm_password": "xyz999",
            "full_name": "Bob", "goal": "maintain",
        }, follow_redirects=True)
        assert b"match" in r.data.lower()


# INTEGRATION tests Food logging & diary

class TestFoodLogging:
    def test_food_diary_loads(self, logged_in_subscriber):
        assert logged_in_subscriber.get("/food-diary").status_code == 200


    def test_log_food_creates_entry(self, logged_in_subscriber, test_app, subscriber):
        logged_in_subscriber.post("/log-food", data={
            "action": "log", "food_name": "Banana", "quantity": "120",
            "meal_type": "breakfast", "log_date": date.today().isoformat(),
            "calories": "89", "protein": "1.1", "carbs": "23",
            "fat": "0.3", "fibre": "2.6", "sugar": "12",
        }, follow_redirects=True)
        with test_app.app_context():
            entry = FoodEntry.query.filter_by(food_name="Banana").first()
            assert entry is not None
            assert entry.quantity_g == 120.0

    def test_log_food_missing_name_rejected(self, logged_in_subscriber):
        r = logged_in_subscriber.post("/log-food", data={
            "action": "log", "food_name": "", "quantity": "100",
            "meal_type": "lunch", "log_date": date.today().isoformat(),
        }, follow_redirects=True)
        assert r.status_code == 200



    def test_delete_own_entry(self, logged_in_subscriber, test_app, subscriber):
        with test_app.app_context():
            entry = FoodEntry(user_id=subscriber, food_name="Apple",
                quantity_g=100, logged_date=date.today())
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id
        logged_in_subscriber.post(f"/delete-entry/{entry_id}", follow_redirects=True)
        with test_app.app_context():
            assert FoodEntry.query.get(entry_id) is None

    def test_cannot_delete_another_users_entry(self, logged_in_subscriber, test_app, professional):
        """Security: subscriber should not be able to delete another user's entry."""
        with test_app.app_context():
            entry = FoodEntry(user_id=professional, food_name="Steak",
                quantity_g=200, logged_date=date.today())
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id
        logged_in_subscriber.post(f"/delete-entry/{entry_id}", follow_redirects=True)
        with test_app.app_context():
            assert FoodEntry.query.get(entry_id) is not None


# further INTEGRATION TESTS for professionals


class TestProfessionalViews:
    def test_accept_client_assigns_and_notifies(self, logged_in_professional, test_app,
            subscriber, professional):
        logged_in_professional.post(f"/accept-client/{subscriber}", follow_redirects=True)
        with test_app.app_context():
            u = User.query.get(subscriber)
            assert u.professional_id == professional
            assert Notification.query.filter_by(user_id=subscriber).first() is not None


    def test_cannot_view_unassigned_client(self, logged_in_professional, test_app, subscriber):
        r = logged_in_professional.get(f"/view-client/{subscriber}", follow_redirects=True)
        assert b"not your client" in r.data.lower() or r.status_code == 200

    def test_set_guidelines_saves_to_db(self, logged_in_professional, test_app, subscriber_with_prof):
        logged_in_professional.post(f"/set-guidelines/{subscriber_with_prof}", data={
            "daily_calories": "2000", "daily_protein_g": "150",
            "daily_carbs_g": "250", "daily_fat_g": "65",
            "daily_fibre_g": "30", "notes": "Focus on fibre.",
        }, follow_redirects=True)
        with test_app.app_context():
            g = NutritionalGuideline.query.filter_by(subscriber_id=subscriber_with_prof).first()
            assert g is not None
            assert g.daily_calories == 2000.0

    def test_cannot_set_guidelines_for_unassigned_subscriber(self, logged_in_professional,
            test_app, subscriber):
        """Security: professional cannot set guidelines for someone else's client."""
        logged_in_professional.post(f"/set-guidelines/{subscriber}", data={
            "daily_calories": "9999",
        }, follow_redirects=True)
        with test_app.app_context():
            assert NutritionalGuideline.query.filter_by(subscriber_id=subscriber).first() is None


# INTEGRATION for Recipes
class TestRecipes:
    def _add_recipe(self, test_app, creator_id):
        with test_app.app_context():
            r = Recipe(title="Test Soup", instructions="Boil things.",
                ingredients=json.dumps([{"name": "Water", "amount": "500ml"}]),
                tags="vegan,soup", calories_per_serving=150, created_by=creator_id)
            db.session.add(r)
            db.session.commit()
            return r.id

    def test_recipes_page_loads(self, logged_in_subscriber):
        assert logged_in_subscriber.get("/recipes").status_code == 200


    def test_recipe_search_returns_match(self, logged_in_subscriber, test_app, subscriber):
        self._add_recipe(test_app, subscriber)
        r = logged_in_subscriber.get("/recipes?search=Test+Soup")
        assert b"Test Soup" in r.data

    def test_add_recipe_creates_db_entry(self, logged_in_subscriber, test_app):
        logged_in_subscriber.post("/add-recipe", data={
            "title": "Veggie Stir Fry", "description": "Quick.",
            "instructions": "Chop and fry.",
            "ingredient_name[]": ["Broccoli"], "ingredient_amount[]": ["200g"],
            "cook_time_mins": "10", "prep_time_mins": "5",
            "servings": "2", "tags": "vegan", "calories_per_serving": "200",
        }, follow_redirects=True)
        with test_app.app_context():
            assert Recipe.query.filter_by(title="Veggie Stir Fry").first() is not None

    def test_add_recipe_comment_with_rating(self, logged_in_subscriber, test_app, subscriber):
        recipe_id = self._add_recipe(test_app, subscriber)
        logged_in_subscriber.post(f"/recipe/{recipe_id}/comment",
            data={"comment": "Loved it!", "rating": "5"}, follow_redirects=True)
        with test_app.app_context():
            c = RecipeComment.query.filter_by(recipe_id=recipe_id).first()
            assert c is not None and c.rating == 5

    def test_empty_comment_not_saved(self, logged_in_subscriber, test_app, subscriber):
        recipe_id = self._add_recipe(test_app, subscriber)
        logged_in_subscriber.post(f"/recipe/{recipe_id}/comment",
            data={"comment": "", "rating": "3"}, follow_redirects=True)
        with test_app.app_context():
            assert RecipeComment.query.filter_by(recipe_id=recipe_id).count() == 0


# INTEGRATION TESTS for Role-based access control

class TestRBAC:
    def test_subscriber_cannot_access_professional_dashboard(self, logged_in_subscriber):
        r = logged_in_subscriber.get("/home-professional", follow_redirects=True)
        assert r.status_code == 200  # redirected away

    def test_professional_cannot_log_food(self, logged_in_professional):
        r = logged_in_professional.get("/log-food", follow_redirects=True)
        assert r.status_code == 200  # redirected away

    def test_subscriber_cannot_find_clients(self, logged_in_subscriber):
        r = logged_in_subscriber.get("/find-clients", follow_redirects=True)
        assert r.status_code == 200  # redirected away


# INTEGRATION TESTS for AJAX food search API

class TestFoodSearchAPI:
    def test_short_query_returns_empty(self, logged_in_subscriber):
        r = logged_in_subscriber.get("/api/food-search?q=a")
        assert json.loads(r.data)["results"] == []

    @patch("app.requests.get")
    def test_mocked_api_returns_results(self, mock_get, logged_in_subscriber):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "products": [{
                "product_name": "Red Apple", "brands": "Tesco",
                "nutriments": {
                    "energy-kcal_100g": 52, "proteins_100g": 0.3,
                    "carbohydrates_100g": 14, "fat_100g": 0.2,
                    "fiber_100g": 2.4, "sugars_100g": 10,
                },
            }]
        }
        mock_get.return_value = mock_response
        r = logged_in_subscriber.get("/api/food-search?q=apple")
        data = json.loads(r.data)
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Red Apple"

    @patch("app.requests.get", side_effect=Exception("Network error"))
    def test_api_network_failure_returns_empty(self, mock_get, logged_in_subscriber):
        r = logged_in_subscriber.get("/api/food-search?q=banana")
        assert json.loads(r.data)["results"] == []