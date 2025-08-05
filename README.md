# CompetitorAnalyzer

This project was built using Angular. It is an app that uses:
 - SerpAPI : Searches the website for competitor companies and scrapes the websites for relevant information
 - PineconeAPI : Upserts the companies found into the database and analyzes how similar they are to Vanguard Charitable
 - OpenAI API : Takes the information scraped and generates a detailed and valuable report on the top competitors found. If no data was able to be scraped, then the agent finds any relevant information regarding the company on secondary source websites or news articles to create the report. 

## Installing Dependencies

In order to run the app, make sure you have the following dependencies installed Angular and all of the dependencies listed in the requirements.txt file in the backend folder.

To install Angular run:

```bash
npm install -g @angular/cli
```

To install everything in the requirements.txt file, run:

```bash
pip install -r requirements.txt
```

or

```bash
python3 -m pip install -r requirements.txt
```

Now you have everything necessary to run the app!

## Development server

To start a local development server, navigate to the frontend folder in the terminal and run:

```bash
ng serve
```

Additionally, to get the backend to run, open a second terminal, navigate to the backend folder, and run:

```bash
uvicorn app:ap --reload
```

Once the frontend server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files. The backend server will run on http://127.0.0.1:8000, but 
there is no need to go to the backend server url. It only needs to run properly in the background for the app to function as intended.

## Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.
