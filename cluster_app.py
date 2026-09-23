from io import BytesIO
from pandas import DataFrame
import streamlit as st
from PIL import Image
from streamlit.dataframe_util import DataFormat
from image_clustering import cluster_image



st.session_state.setdefault("curr", None)
st.session_state.setdefault("img", None)
st.session_state.setdefault("width", 1000)
st.session_state.setdefault("height", 1000)
st.session_state.setdefault("isProcessed", False)
st.session_state.setdefault("fileName", "untitled.png")
# st.session_state.setdefault("data")

ids = {
    "RGB": "rgb",
    "Variable Hue": "hsv",
    "Variable Brightness": "h_sv"
}

def sync_height_to_width():
    st.session_state.heightSlider = st.session_state.widthSlider * st.session_state.height // st.session_state.width

def sync_width_to_height():
    st.session_state.widthSlider = st.session_state.heightSlider * st.session_state.width // st.session_state.height

# def get_image_data():
#     # print(img)
#     file = BytesIO()
#     print(img)
#     img.save(file, "jpeg")
#     # print(file)
#     return file

# if 'curr' not in st.session_state:
#     st.session_state.curr = None
#     st.session_state.img = None
#     st.session_state.width = 1000
#     st.session_state.height = 1000

    # st.session_state['currWidth'] = st.session_state['currHeight'] = 128
    # st.session_state['modified'] = False

# st.session_state.height

num_colors = st.sidebar.slider("Num colors", 2, 32)
mode = ids[st.sidebar.selectbox("Mode to use", ["RGB", "Variable Hue", "Variable Brightness"])]
use_pixel_art = st.sidebar.checkbox('Generate pixel art')

if use_pixel_art:
    width = st.sidebar.slider("Pixel Width", 2, 512, key="widthSlider", on_change=sync_height_to_width)
    height = st.sidebar.slider("Pixel Height", 2, 512, key = "heightSlider", on_change=sync_width_to_height)
    # st.session_state['width'], st.session_state['height'] = width, height
    pixel_size= (width,height)
else:
    # height = width = 2
    pixel_size = None

img_file = st.sidebar.file_uploader("Upload an image", "image")
button = st.sidebar.button(
    "Use magic on image", 
    icon="✨", 
    disabled=img_file == None,
)

if button:
    st.session_state.img = cluster_image(
        Image.open(img_file), 
        num_colors,
        mode,
        pixel_size=pixel_size,
    )
    st.session_state.isProcessed = True
    st.session_state.processedImg = BytesIO()
    st.session_state.img.save(st.session_state.processedImg, "png")
    if img_file != None:
        name = img_file.name.split(".")[0]
        if pixel_size == None:
            st.session_state.fileName = name + " " + str(num_colors) + " colors.png"
        else:
            st.session_state.fileName = name + " pixel art.png"
        # print(st.session_state.fileName)
if img_file != None:
    if st.session_state.curr != img_file.name:
        st.session_state.curr = img_file.name
        temp = Image.open(img_file)
        st.session_state.img = temp
        st.session_state.width, st.session_state.height = temp.size
        st.session_state.isProcessed = False
    st.write(st.session_state.img)
    st.sidebar.download_button(
        label="Download finished image",
        data=st.session_state.processedImg,#st.session_state.img.tobytes(),
        file_name=st.session_state.fileName,
        disabled=not st.session_state.isProcessed,
    )
# else:
#     st.session_state['curr'] = None
#     st.session_state['img'] = None


st.divider()

# palette = {
#     "Color": [1, 2, 3],
#     "Red": [127, 69, 42],
#     "Green": [255, 0, 100],
#     "Blue": [0, 127, 255],
#     "Hex code": ["#abcdef", "#123456", "#676767"]
    
# }

# st.table(DataFrame(palette))
