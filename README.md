# CompetitorAnalyzer

This project was built using Angular. It is an app that uses:
 - SerpAPI : Searches the website for competitor companies and scrapes the websites for relevant information
 - PineconeAPI : Upserts the companies found into the database and analyzes how similar they are to Vanguard Charitable
 - OpenAI API : Takes the information scraped and generates a detailed and valuable report on the top competitors found. If no data was able to be scraped, then the agent finds any relevant information regarding the company on secondary source websites or news articles to create the report. 

## Development server

To start a local development server, run:

```bash
ng serve
```

Additionally, to get the backend to run, first open a second terminal, navigate to the backend folder, and run:

```bash
uvicorn app:ap --reload
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.