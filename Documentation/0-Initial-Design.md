Overview:
For this project we will be creating a website to support people in eating healthier by providing diet & nutritional advice as well as promoting home cooking. The website will allow people to subscribe to the service record their diet, visualise their information and receive feedback from professionals. There will also be recommendations and tutorials for home cooking recipes.

Research into similar websites:
MtFitnessPal- MyFitnessPal's  home page features a box for Calories that have been eaten that day, with boxes for grams of carbs, fats and protein eaten that day. At the top is the option to scroll to different days. At the bottom of the page, if you scroll down, there is a diary with boxes for 'Breakfast', 'Lunch', 'Dinner' and 'Snacks', with options to log food for each of them.


Highest Priority Features:
Allow subscribers to log food intake in a ‘food diary’. 

Allow users to look back at subscriber’s food diary. 

Contain baseline nutrition guidelines that the user can compare to their own dietary habits. 

System should offer clear feedback on user’s diets 

Individual profiles for subscribers that allow for the storage of their dietary information. 

A log in system. 

Accounts for health professionals that can link with subscribers as clientele. 

Professionals should be able to view client information. 

Professionals should be able to advise clients 


Medium Priority Features:

Users should be able to search for recipes based on their ingredients. 

Users should be able to log which recipes they’ve tried and mark favourites. 

Display picture and media when users browse recipes. 

Users should be able to search for recipes by ingredients. 

System should include a catalogue of easy to prepare meals. 

Subscribers should be able to visualise the number of nutrients in their food. 

Graph that shows subscriber caloric intake by day over at least a 2-week period. 

Allergen check. 


Lowest Priority Features

Users should be able to leave comments and ratings on recipes. 

System could be able to offer specific recipe recommendations based on user preferences/dietary habits – For example if the user doesn’t log themselves eating many vegetables, then more vegetable-heavy options would be recommended, or if a user marks a dish with a high rating or as a favourite, then similar meals to that would be recommended (this may involve having to categorise the meals in some way, or potentially just recommending meals with similar ingredients). 

Terminal tests:

Test 1: Users must be able to create an account

Test 2: Users must be able to login with their username and password

Test 3: Users must be able to choose whether to make a client or professional account

Test 4: Clients must be able to create a food diary

Test 5: Users must be able to log in to the app and note down the food they have eaten within 1 minute.

Test 6: Professionals must be able to view their client's food diaries.

Test 7: There must be functionality to search through recipes from an API

Test 8: Users must be able to see an estimate of cost for each recipe.

Test 9: Users must be able to see an estimate of calories for each recipe.

Test 10: Users must be able to see an estimate of nutrients for each recipe.

Test 11: Users must be able to search for recipes by ingredients.

Test 12: Clients and professionals must have a way to communicate with each other.

Test 13: WebApp must have data visualisation for a users calories in the form of a bar chart.

Test 14: When users log their food, it should be sorted into Breakfast, Lunch, Dinner and Snacks


Diagrams:

ERD as reference for creating the database to be used in project. 

![ERD diagram](<Initial-Design-Images/image.png>)

Diagram showing how pages interact with each other

![Webpages](<Initial-Design-Images/Webpages.png>)


Wireframes:

It is important to create wireframes as a reference for development. 

Home pages for client: 
![Home page clients](<Initial-Design-Images/Client home page wireframe.png>)

Home page for professionals: 
![Professional home page](<Initial-Design-Images/Proffesional home page wireframe.png>)

Login or create account: 

 ![Login/create account](<Initial-Design-Images/Login or create acc wireframe.png>)

Login page: 

![Login page](<Initial-Design-Images/Login page.png>)

Create client: 

![Create client](<Initial-Design-Images/Create client.png>)

Create professional: 

![Create professional](<Initial-Design-Images/Create Professional.png>)

Speak to client’s page: 

![Speak to clients](<Initial-Design-Images/Speak to clients wireframe.png>)

Find client's page: 

![Find clients](<Initial-Design-Images/Find clients page.png>)

Accept client page: 

![Accept client](<Initial-Design-Images/Accept client page.png>)

Message client page: 

![Message clients](<Initial-Design-Images/Screenshot from 2026-05-08 14-39-26.png>)

Speak to professionals page: 

![Speak to professionals](<Initial-Design-Images/Speak to professionals wireframe.png>)

Raise new issue page: 

![Raise issue](<Initial-Design-Images/Raise issue.png>)

Message professionals page: 

![message professional](<Initial-Design-Images/Message professionals wireframe.png>)

Send message page: 

![Send message](<Initial-Design-Images/Messsages.png>)
 
View clients food diary, select client page: 

![Select client](<Initial-Design-Images/Find clients page-1.png>)

Search for recipes page: 

![Search for recipes](<Initial-Design-Images/Search recipes wireframe.png>)

View individual recipes page 1: 

![View recipes page 1](<Initial-Design-Images/Screenshot from 2026-05-08 14-44-02.png>)

View individual recipe middle pages: 

![Recipe middle](<Initial-Design-Images/Recipes middle pages wireframe.png>)

View recipes last page: 

![Recipe last](<Initial-Design-Images/Recipes last page wireframe.png>)

Recipes comments: 

![Recipe comments](<Initial-Design-Images/Recipe comments page.png>)

Give rating page: 

![Rating](<Initial-Design-Images/Give rating wireframe.png>)

 

There are a lot of similarities between different pages which can be collected in base templates. 

One is the home button which will go to the client/professional home page depending on what account is signed in. This is on all pages. 

There is also the page with 2 decisions which shows up frequently. 

The home page between clients and professionals is very similar so inheritance could likely be used there. 