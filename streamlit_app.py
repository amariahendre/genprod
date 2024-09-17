import streamlit as st
import base64
import requests

# Citirea cheii API din secrets.toml stocat în Streamlit Cloud
def get_api_key():
    return st.secrets["openai"]["api_key"]

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# OpenAI API request function
def analyze_image(api_key, base64_image, prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt  # Include the user's custom prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    return response.json()

# Function to extract text from the API response
def extract_text_from_response(response):
    try:
        return response['choices'][0]['message']['content']
    except KeyError:
        return "Error: Could not extract text from the response."

# Streamlit App
def main():
    st.title("GenProd – generare de nume și descrieri pentru produse")

    # Mutăm instrucțiunile în sidebar
    with st.sidebar:
        st.header("Despre această aplicație")
        st.markdown("""
        Această aplicație permite utilizatorilor să încarce imagini cu produse și să genereze automat un nume și o descriere detaliată pentru produsul respectiv. 
        Generarea se face utilizând modelul OpenAI GPT-4.

        ### Instrucțiuni de utilizare:
        1. Introduceți cheia dvs. OpenAI API.
        2. Încărcați o imagine a produsului pentru care doriți să generați o descriere.
        3. Completați detaliile suplimentare despre produs (opțional) pentru a îmbunătăți descrierea generată.
        4. Apăsați butonul **Generează** pentru a primi un nume și o descriere pentru produsul încărcat.
        """)

    # Introducerea cheii API și detaliilor produsului pe prima pagină
    st.subheader("Introduceți datele produsului")

    # Input pentru cheia API
    api_key = st.text_input("Introduceți cheia dvs. OpenAI API:", type="password")

    # Input pentru informații suplimentare
    user_input = st.text_area("Introduceți informații suplimentare despre produs:", 
                               placeholder="Ex: piata tinta, materialul produsului, utilizarea etc.")

    # Widget pentru încărcarea imaginii
    uploaded_image = st.file_uploader("Alegeți o imagine...", type=["jpg", "jpeg", "png"])

    # Buton pentru generare
    generate_button = st.button("Generează")

    # Afișarea imaginii imediat după upload pe prima pagină
    if uploaded_image:
        st.image(uploaded_image, caption="Imagine încărcată", use_column_width=True)

    # Dacă se apasă butonul de generare
    if generate_button and uploaded_image and api_key:
        # Codificarea imaginii
        base64_image = encode_image(uploaded_image)

        # Crearea promptului folosind șablonul oferit
        prompt = f"""
        Esti expert în marketing. Generează nume și descriere pentru acest produs. 
        Ia în considerare și următoarele informații: {user_input}.
        
        Exemplu:
        Denumire: Cană Albă pentru Copii cu Prințesă Roz și Iepuraș - Decor Fimo, 360 ml.
        Descriere: Această cană albă de 360 ml este decorată manual cu o prințesă adorabilă purtând o rochiță roz și ținând un iepuraș gri pufos, realizată din Fimo. 
        Fetița poartă o coroniță elegantă, iar fiecare detaliu, de la fundițele roz și până la rochia delicată cu volane, este lucrat cu mare atenție. 
        Decorată cu cristale strălucitoare, cana adaugă un strop de magie fiecărei băuturi preferate. Ideală pentru cei mici, această cană este perfectă pentru băuturi calde sau reci, oferind un cadou unic și fermecător pentru orice ocazie!
        """

        # Apelul API și afișarea rezultatului
        with st.spinner("Se analizează imaginea..."):
            result = analyze_image(api_key, base64_image, prompt)

        # Extrage și afișează textul din răspunsul API
        if result:
            extracted_text = extract_text_from_response(result)
            st.subheader("Răspunsul de la AI:")
            st.write(extracted_text)
        else:
            st.error("Eroare: Nu s-a putut obține analiza de la API.")
    elif generate_button:
        st.warning("Vă rugăm să încărcați o imagine și să introduceți cheia API.")

if __name__ == "__main__":
    main()
