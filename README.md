# M.A.R.S- Metric-Augumented-Retrieval-System
A pipeline that takes any furniture image (Amazon, photo, etc.), detects the furniture, retrieves its real-world dimensions from a database, generates a 3D model automatically, and exports it as a VR-ready file . Fully automated end to end.

Refer to documentation for further information + results.



M.A.R.S. (Metric-Augmented Retrieval System) User Manual

Prerequisites
Before starting, ensure you have:

A Google Account with Google Drive access.
A Gemini API Key (obtained via Google AI Studio).
A target furniture image (e.g., .jpg, .png, or .webp).

Step 1: Environment Setup & Mounting Google Drive
Open your Colab notebook and run the first cell to mount your Google Drive. 


Step 2: Configuring Your Gemini API Key
To prevent exposing your raw API key in the code, utilize Colab's built-in Secrets utility (the key icon in the left-hand sidebar).

Click the Secrets (Key icon) on the left menu.
Add a new secret with the Name: GEMINI_API_KEY.
Paste your actual API key into the Value field.
Toggle on Notebook access.

Run the api_key cell to initialize the environment variable:


Step 3: Blender Engine Installation
Because standard Colab environments lack Blender dependencies, you must run the cell that downloads and extracst the Linux build of Blender to run your background execution scripts.


Step 4: Adding Your Input Image 
Run the DEVELOPMENT ZONE cell and click Add Files to add an image of a furniture(preferably with no background)
This cell feeds the input image into the Gemini Vision API to parse features, queries ikea_dimensions_rag.json for scale grounding, and triggers 3D generation engine
What happens behind the scenes:

Pass 1 (Vision): Gemini evaluates target_chair.jpg to identify the product style, classify the component counts, and structure a text token map.
Pass 2 (RAG Search): The orchestrator matches the product profile against ikea_dimensions_rag.json to lock down global scale parameters.
Pass 3 (Procedural Build): The values are securely routed to mars_lib.py, which maps components relative to a single moveable hierarchy, applying safety boundary checks and automated spacing.

Step 6: Fetching Your 3D Output
Once the cell finish execution successfully, navigate to your Google Drive directory via the file browser or your desktop file manager:

Open your Google Drive.
Go to the mars/ folder.
Locate the  outputs/ subfolder
Download the generated .glb asset 


Workflow Video 
https://github.com/user-attachments/assets/c03d5f15-63aa-4b42-a778-8b1284a59e82

