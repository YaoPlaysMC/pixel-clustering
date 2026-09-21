import streamlit as st
from PIL import Image
from image_clustering import cluster_image


ids = {
    "RGB": "rgb",
    "Variable Hue": "hsv",
    "Variable Brightness": "h_sv"
}

def sync_height_to_width():
    st.session_state.heightSlider = st.session_state.widthSlider * st.session_state.height // st.session_state.width

def sync_width_to_height():
    st.session_state.widthSlider = st.session_state.heightSlider * st.session_state.width // st.session_state.height



# if 'curr' not in st.session_state:
#     st.session_state.curr = None
#     st.session_state.img = None
#     st.session_state.width = 1000
#     st.session_state.height = 1000
st.session_state.setdefault("curr", None)
st.session_state.setdefault("img", None)
st.session_state.setdefault("width", 1000)
st.session_state.setdefault("height", 1000)
    # st.session_state['currWidth'] = st.session_state['currHeight'] = 128
    # st.session_state['modified'] = False

# st.session_state.height

num_colors = st.slider("Num colors", 2, 32)
mode = ids[st.selectbox("Mode to use", ["RGB", "Variable Hue", "Variable Brightness"])]
use_pixel_art = st.checkbox('Generate pixel art')

if use_pixel_art:
    width = st.slider("Pixel Width", 2, 512, key="widthSlider", on_change=sync_height_to_width)
    height = st.slider("Pixel Height", 2, 512, key = "heightSlider", on_change=sync_width_to_height)
    # st.session_state['width'], st.session_state['height'] = width, height
    pixel_size= (width,height)
else:
    height = width = 2
    pixel_size = None

img_file = st.file_uploader("Upload an image", "image")
button = st.button(
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

if img_file != None:
    if st.session_state.curr != img_file.name:
        st.session_state.curr = img_file.name
        temp = Image.open(img_file)
        st.session_state.img = temp
        st.session_state.width, st.session_state.height = temp.size
    st.write(st.session_state.img)
# else:
#     st.session_state['curr'] = None
#     st.session_state['img'] = None
    
