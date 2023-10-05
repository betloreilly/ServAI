import streamlit as st
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from audiorecorder import audiorecorder
from PIL import Image
import openai
from tools import Waiter, TotalAmount
from gtts import gTTS
from io import BytesIO
import os
from dotenv import dotenv_values
from langchain.schema import SystemMessage
##############################
### initialize agent #########
##############################
tools = [ TotalAmount() ,Waiter() ]
config = dotenv_values('conf.env')
openai_key = config['OPENAI_API_KEY']
ASTRA_DB_KEYSPACE = config['ASTRA_KEYSPACE']

conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=10,
    return_messages=True
)

llm = ChatOpenAI(
    openai_api_key=openai_key,
    temperature=0,
    model_name="gpt-4"
)

 
system_message = SystemMessage(content="You are a waiter called Elsa for the restaurant Nectar & Nosh and you need to check what is available in the menu and you can provide concise responses. "
                                       "You help with customer's questions related to the options in the menu and ask if they need anything else "
                                       "and you always provide total cost of the order at the end"
                                       )


agent = initialize_agent(
    agent="chat-conversational-react-description",
    tools=tools,
    llm=llm,
    max_iterations=5,
    verbose=True,
    memory=conversational_memory,
    early_stopping_method='generate',
     agent_kwargs={
        "system_message": system_message.content
    }
)


# set title
st.title('WElCOME TO Nectar & Nosh!')
image = Image.open('/Users/betuloreilly/demos/ServAI/menu.png')
st.image(image)
audio = audiorecorder("How can I help you today!", "Recording...")

if len(audio) > 0:
    # To play audio in frontend:
    st.audio(audio.tobytes())
     # To save audio to a file:
    wav_file = open("test.mp3", "wb")
    wav_file.write(audio.tobytes())

    audio_file= open("/Users/betuloreilly/demos/ServAI/test.mp3", "rb")
    user_question = openai.Audio.transcribe("whisper-1", audio_file)

    ##############################
    ### compute agent response ###
    ##############################
    if user_question and user_question != "":
        sound_file = BytesIO()
        with st.spinner(text="In progress..."):
            response = agent.run('{}, {}'.format(user_question, user_question))
            #st.write(user_question)
            #st.write(response)
            # Initialize gTTS with the text to convert
            speech = gTTS(response,tld='us',slow=False)

            # Save the audio file to a temporary file
            speech_file = 'speech.mp3'
            speech.save(speech_file)

            # Play the audio file
            os.system('afplay ' + speech_file)