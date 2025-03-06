# U-L-P-SearchApi

Basically you put your U:L:P .txt files into uploads and the Python code will take them all and create an API with filters.

# IMAGES
![image](https://github.com/user-attachments/assets/e1de82e9-b436-45fe-a5bd-3b3c4e424902)
![image](https://github.com/user-attachments/assets/d9bec950-b7b0-4eea-8f31-5072392d9209)

# SETUP 

- Python (PIP)
  - 1- Open cmd and go to the project folder using CD on windows or linux and run the following command.
  - 2- pip install -r requirements.txt
  - 3- After the packages are installed in folder uploads put the U:L:P Logs in .txt.
  - 4- Then go back to cmd in the folder and run `python app.py`.
  - 5- Finally in the browser go to `http://127.0.0.1:8080/search?filter=YOUR_QUERY`
    - Example: http://127.0.0.1:8080/search?filter=sso.crunchyroll.com

# IMPORTANT

- It was made in order to see the impact of leaking information that can be visible to anyone, the owner is not responsible for misuse.
