import streamlit as st
from PIL import Image, ImageDraw
import base64
from io import BytesIO
import tkinter as tk
from PIL import ImageTk
from PIL import ImageFont
import pandas as pd

def mark_coordinates(image_path):
    # Function to mark coordinates for participant name on the image using Tkinter
    coordinates = []

    def close_window():
        win.quit()

    def save_coordinates():
        nonlocal coordinates
        nonlocal btn_done
        btn_done["state"] = "disabled"
        btn_done.update()
        win.quit()

    def get_coordinates(event):
        x = event.x
        y = event.y
        coordinates.append((x, y))
        # Draw a small red dot to mark the coordinate
        canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill='red')

    # Open the image using Pillow
    img = Image.open(image_path)
    img_resized = img.resize((800, 600))  # Image for proper display

    # Displays the image in a Tkinter window
    win = tk.Tk()
    win.title("Mark Coordinates (click left button of mouse where participant's name should be marked and then click Done button)")

    canvas = tk.Canvas(win, width=img_resized.width, height=img_resized.height)
    canvas.pack()

    tk_img = ImageTk.PhotoImage(img_resized)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # Bind left mouse button click event to get_coordinates function
    canvas.bind("<Button-1>", get_coordinates)

    # Add a button to save the coordinates
    btn_done = tk.Button(win, text="Done", command=save_coordinates)
    btn_done.pack()

    # Add a button to close the window
    btn_close = tk.Button(win, text="Close", command=close_window)
    btn_close.pack()

    # Wait for the user to mark coordinates
    win.mainloop()

    return coordinates

def generate_certificate(image_path, participant_name, coordinates, font_size):
    # Function to generate certificate with participant name at specified coordinates
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Iterate through each set of coordinates
    for coord in coordinates:
        x, y = coord  # Extract coordinates
        draw.text((x * img.width / 800, y * img.height / 600), participant_name, fill='black', font=ImageFont.truetype("arial.ttf", font_size))

    # Display the modified image
    st.image(img, caption='Generated Certificate', use_column_width=True)

    # Provide a download link for the generated certificate
    st.markdown(get_image_download_link(img), unsafe_allow_html=True)

def get_image_download_link(image):
    # Function to generate download link for the image
    buffered = BytesIO()
    image.save(buffered, format="PDF")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="certificate.pdf">Download Certificate</a>'
    return href

def generate_multiple_certificates(participant_names, certificate_image, font_size, coordinates):
    # Function to generate multiple certificates
    img = Image.open(certificate_image)
    draw = ImageDraw.Draw(img)

    for i, participant_name in enumerate(participant_names):
        generate_certificate(certificate_image, participant_name, coordinates, font_size)
        st.write('\n')

def main():
    st.title('Automated Certificate Generator')

    # Sidebar navigation
    selected_page = st.sidebar.radio('Navigation', ['Home', 'Single Certificates', 'Multiple Certificates'])

    if selected_page == 'Single Certificates':
        st.sidebar.write('Single Certificate Options')
        participant_name = st.text_input("Enter Participant's Name:")
        font_size = st.slider("Select Font Size", 10, 100, 30, 1)  # Moved slider here

        certificate_image = st.file_uploader("Upload Certificate Template:", type=["png", "jpg", "jpeg"])

        if certificate_image is not None and st.button("Generate Certificate"):
            coordinates = mark_coordinates(certificate_image)
            generate_certificate(certificate_image, participant_name, coordinates, font_size)

    elif selected_page == 'Multiple Certificates':
        st.sidebar.write('Multiple Certificate Options')

        uploaded_file = st.file_uploader("Upload a file with participants name", type=["xlsx", "csv", "txt"])

        if uploaded_file is not None:
            if uploaded_file.type == 'text/plain':  # For TXT files
                participant_names = uploaded_file.getvalue().decode("utf-8").splitlines()
            else:  # For CSV and XLSX files
                df = pd.read_excel(uploaded_file) if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' else pd.read_csv(uploaded_file)
                participant_names = df.iloc[:, 0].tolist()

            num_certificates = len(participant_names)
            font_size = st.slider("Select Font Size", 10, 100, 30, 1)  # slider for font size

            certificate_image = st.file_uploader("Upload Certificate Template:", type=["png", "jpg", "jpeg"])

            if certificate_image is not None and st.button("Generate Certificates"):
                st.write("Mark coordinates for all participants")
                coordinates = mark_coordinates(certificate_image)
                generate_multiple_certificates(participant_names, certificate_image, font_size, coordinates)

    else:
        st.write('Welcome to Automated Certificate Generator!')
        # Implementing  home page content

if __name__ == '__main__':
    main()
