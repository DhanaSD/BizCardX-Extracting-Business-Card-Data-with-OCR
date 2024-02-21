#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image,ImageDraw
import pandas as pd
import numpy as np
import re
import pymysql
import io

st.markdown("<h1 style='text-align: center; color: #0066cc;font-size: 30px;'>BizCardX: Extracting Business Card Data with OCR</h1>",
            unsafe_allow_html=True)
# CREATING OPTION MENU
option = st.radio(':violet[**Select your option**]',("Home", "Upload & Preview","Edit&Delete"),horizontal=True)

if option == "Home":
    c=Image.open(r"C:\Users\acer\Downloads\busi_card.jfif")
    st.image(c)
   
    st.markdown(
    f"<h1 style='color:#cc3399; font-size: 20px;'>Technologies Used : Python,easy OCR, Streamlit, SQL, Pandas</h1>",
    unsafe_allow_html=True,) 
    
    st.markdown(
    f"<h1 style='color:#cc3399; font-size: 20px;'>About : Bizcard is a Python application designed to extract information
        from business cards.</h1>",
    unsafe_allow_html=True,)
    
    st.markdown(
    f"<h1 style='color:#cc3399; font-size: 20px;'>The main purpose of Bizcard is to automate the process of extracting key
        details from business card images, such as the name, designation, company, contact information, and other relevant data.
        By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from
        the images.</h1>",
    unsafe_allow_html=True,)
    
#-----------------------------Data Extraction and Upload Zone-------------------------------------------------------------------------------------------------------------------------------------------------

def extract_information(text):
 
 data={'Card_holder':[],
      'Designation':[],
      'Company_name':[],
      'Mobile_No':[],
      'E_mail':[],
      'Website':[],
      'Area':[],
      'City':[],
      'State':[],
      'Pin_code':[]}
 for ind, i in enumerate(result):
  if ind==0:
    data["Card_holder"].append(i)
  elif ind == 1:
     data["Designation"].append(i)
  elif ind == len(result)-1:
     data["Company_name"].append(i)
  elif "-" in i:
     data["Mobile_No"].append(i)
     if len(data["Mobile_No"]) == 2:
       data["Mobile_No"] = " & ".join(data["Mobile_No"])
  elif "@" in i:
      data["E_mail"].append(i)
  elif "www " in i.lower() or "www." in i.lower():
      data["Website"].append(i)
  elif "WWW" in i:
      data["Website"].append(result[ind-1] + "." + result[ind])
  if re.findall("^[0-9].+, [a-zA-Z]+", i):
       data["Area"].append(i.split(",")[0])
  elif re.findall("[0-9] [a-zA-Z]+", i):
       data["Area"].append(i)
  match1 = re.findall(".+St , ([a-zA-Z]+).+", i)
  match2 = re.findall(".+St,, ([a-zA-Z]+).+", i)
  match3 = re.findall("^[E].*", i)
  if match1:
     city = match1[0]
     data["City"].append(city)
  elif match2:
     city = match2[0]
     data["City"].append(city)
  elif match3:
      city = match3[0]
      data["City"].append(city)
  state_match = re.findall("[a-zA-Z]{9} +[0-9]", i)
  if state_match:
      data["State"].append(i[:9])
  elif re.findall("^[0-9].+, ([a-zA-Z]+);", i):
      data["State"].append(i.split()[-1])
  if len(data["State"]) == 2:
      data["State"].pop(0)
  if len(i) >= 6 and i.isdigit():
      data["Pin_code"].append(i)
  elif re.findall("[a-zA-Z]{9} +[0-9]", i):
      data["Pin_code"].append(i[10:])

 return(data)


if option == "Upload & Preview":
 
    image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")
    
    if image is not None:
        input_image = Image.open(image)
        # Setting Image size
        
        st.image(input_image, width=350, caption='Uploaded Image')
        st.markdown(
            f'<style>.css-1aumxhk img {{ max-width: 300px; }}</style>',
            unsafe_allow_html=True
        )
    
    reader = easyocr.Reader(['en'], gpu=False)        
        
    try:
     if isinstance(image, str):
        image = Image.open(image)
     elif isinstance(image, Image.Image):
        image = image
     else:
        image = Image.open(image)
         
        image_array = np.array(image)
        text_read = reader.readtext(image_array)
        st.write(text)
        st.write("")    
        df = []
        for i in text:
          df.append(i)
    except:
       st.write("")      
    
    col1,col2,col3,col4=st.columns(4) 
    with col1:
        View = st.button('**View Dataframe of image**', key='View_button')
    with col2:  
        Upload = st.button('**Upload to MySQL DB**', key='upload_button')
 
    if View:
    
        result = extract_information(text) 
        df=pd.DataFrame(result,index=[0])
        st.dataframe(df)  
    

 
    if Upload:
            result = extract_information(text) 
               
            df=pd.DataFrame(result,index=[0])
       
            myconnection=pymysql.connect(host='127.0.0.1',user='root',passwd='Geethu!20D')
            cur=myconnection.cursor() 
            cur.execute("create database if not exists Bizcards")
            myconnection=pymysql.connect(host='127.0.0.1',user='root',passwd='Geethu!20D',database='Bizcards')
            cur=myconnection.cursor()   
            cur.execute("create table if not exists card_holder_details(Name text,Designation varchar(255),Company_Name varchar(255),Mobile_No varchar(255),Email varchar(255),Website varchar(255),Address varchar(500))")  
            sql = "insert  into card_holder_details(Name,Designation,Company_Name,Mobile_No,Email,Website,Address) values (%s,%s,%s,%s,%s,%s,%s)"
            for i in range(0,len(df)):
                cur.execute(sql,tuple(df.iloc[i]))
                myconnection.commit()   
            st.markdown(
                f"<h1 style='color:#539165; font-size: 24px;'>Data sucessfully Uploaded to MySQL </h1>",
            unsafe_allow_html=True,)  
            
#-------------------------------Edit and Delete zone---------------------------------------------------
if option=='Edit&Delete' : 
    col1,col2=st.columns(2)       
    with col1:
        st.subheader(':red[Edit option]')
     
        # Connect to the database
        myconnection=pymysql.connect(host='127.0.0.1',user='root',passwd='Geethu!20D',database='Bizcards')
        cur=myconnection.cursor()   

            
            # Execute the query to retrieve the cardholder data
        cur.execute("SELECT Name FROM card_holder_details")

            # Fetch all the rows from the result
        rows = cur.fetchall()

            # Take the cardholder name
        names = []
        for row in rows:
            names.append(row[0])

            # Create a selection box to select cardholder name
        cardholder_name = st.selectbox("**Select a Cardholder name to Edit the details**", names, key='cardholder_name')

            # Collect all data depending on the cardholder's name
        cur.execute( "SELECT Name, Company_Name, Designation, Mobile_No, Email, Website, Address FROM card_holder_details WHERE Name=%s", (cardholder_name,))
        col_data = cur.fetchone()

            # DISPLAYING ALL THE INFORMATION
        Name= st.text_input("Name", col_data[0])    
        Company_Name = st.text_input("Company_Name", col_data[1])
        Designation = st.text_input("Designation", col_data[2])
        Mobile_No = st.text_input("Mobile_No", col_data[3])
        Email = st.text_input("Email", col_data[4])
        Website = st.text_input("Website", col_data[5])
        Address = st.text_input("Address", col_data[6])
            # Create a session state object
        class SessionState:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
        session_state = SessionState(data_update=False)
            
            # Update button
        st.write('Click the :red[**Update**] button to update the modified data')
        update = st.button('**Update**', key = 'update')

            # Check if the button is clicked
        if update:
                session_state.data_update = True

            # Execute the program if the button is clicked
        if session_state.data_update:

                # Update the information for the selected business card in the database
                cur.execute(
                  "UPDATE card_holder_details SET Company_Name = %s, Designation = %s, Mobile_No = %s, Email = %s,Website = %s, Address=%s WHERE Name=%s",(Company_Name, Designation, Mobile_No, Email, Website, Address,Name))
                
                myconnection.commit()

                st.success("successfully Updated.")

                # Close the database connection
                myconnection.close()
                
                session_state.data_update = False
      
    with col2:
        
        st.subheader(':red[Delete option]')

        
            # Connect to the database
        myconnection=pymysql.connect(host='127.0.0.1',user='root',passwd='Geethu!20D',database='Bizcards')
        cur=myconnection.cursor()   

            # Execute the query to retrieve the cardholder data
        
        cur.execute("SELECT Name FROM card_holder_details")

            # Fetch all the rows from the result
        del_name = cur.fetchall()

            # Take the cardholder name
        del_names = []
        for row in del_name:
                del_names.append(row[0])

            # Create a selection box to select cardholder name
        delete_name = st.selectbox("**Select a Cardholder name to Delete the details**", del_names, key='delete_name')

            # Create a session state object
        class SessionState:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
        session_state = SessionState(data_delet=False)

            # Delet button
        st.write('Click the :red[**Delete**] button to Delete selected Cardholder details')
        delet = st.button('**Delete**', key = 'delet')

            # Check if the button is clicked
        if delet:
                session_state.data_delet = True

            # Execute the program if the button is clicked
        if session_state.data_delet:
                cur.execute(f"DELETE FROM card_holder_details WHERE Name='{delete_name}'")
                myconnection.commit()

                st.success("Successfully deleted from database.")

                # Close the database connection
                myconnection.close()

                session_state.data_delet = False

        
        

        
        
        

    


