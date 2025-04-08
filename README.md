To run this code, clone to your local machine using <br>
```
git clone https://github.com/leahtara/cbt_app.git
cd cbt_app
```
Now you want to create a python environment called venv<br>
```
python3 -m venv venv
```
Then activate it:<br>
```
source venv/bin/activate
```
Now install the packages:<br>
```
pip install -r requirements.txt
```
Create a .env file for your api key. (Remember to replave 'YOUR_API_KEY' with your google ai studio api key<br>
```
touch .env 
echo "GEMINI_API_KEY=YOUR_API_KEY"
```
Now run the code:<br>
```
streamlit run app.py
```
<br>