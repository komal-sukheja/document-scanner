import cv2
import numpy as np
import streamlit as st
from PIL import Image
import io

# ============================================================================
# CONFIGURATION
# ============================================================================
class Config:
    """Application configuration constants"""
    SUPPORTED_FORMATS = ["jpg", "png", "jpeg"]
    CANNY_THRESHOLD1 = 75
    CANNY_THRESHOLD2 = 200
    GAUSSIAN_BLUR = (5, 5)
    CONTOUR_APPROX_FACTOR = 0.02

# ============================================================================
# CORE IMAGE PROCESSING FUNCTIONS
# ============================================================================

def order_points(pts):
    """
    Order corner points in clockwise order starting from top-left
    Returns: [top-left, top-right, bottom-right, bottom-left]
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left (smallest sum)
    rect[2] = pts[np.argmax(s)]   # bottom-right (largest sum)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def four_point_transform(image, pts):
    """
    Apply perspective transformation to get bird's eye view of document
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Calculate width and height of new image
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    
    # Destination points for the transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    # Compute and apply perspective transform
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def detect_document_contour(image):
    """
    Detect document boundary using edge detection and contour approximation
    Returns: (contour, edges_image)
    """
    # Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, Config.GAUSSIAN_BLUR, 0)
    
    # Edge detection
    edges = cv2.Canny(gray, Config.CANNY_THRESHOLD1, Config.CANNY_THRESHOLD2)
    
    # Find contours and sort by area
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    # Find the first 4-sided contour (assumed to be document)
    doc_contour = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, Config.CONTOUR_APPROX_FACTOR * peri, True)
        if len(approx) == 4:
            doc_contour = approx
            break
    
    return doc_contour, edges

def apply_noise_reduction(image, kernel_size):
    """
    Apply morphological operations to reduce noise
    """
    if kernel_size > 0:
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        # Closing: removes small black holes
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # Opening: removes small white noise
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return image

def apply_scan_mode(warped_image, mode, noise_reduction):
    """
    Apply different scanning modes to the warped image
    """
    warped_gray = cv2.cvtColor(warped_image, cv2.COLOR_RGB2GRAY)
    
    if mode == "Black & White":
        # Adaptive thresholding for clean B&W output
        scanned = cv2.adaptiveThreshold(
            warped_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2)
        scanned = apply_noise_reduction(scanned, noise_reduction)
        return scanned
    
    elif mode == "Enhanced B&W":
        # More aggressive thresholding for documents with backgrounds
        scanned = cv2.adaptiveThreshold(
            warped_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 15, 10)
        scanned = apply_noise_reduction(scanned, noise_reduction)
        return scanned
    
    return warped_image

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def draw_corners(image, corners, radius=10):
    """
    Draw corner points and boundary on image for visualization
    """
    output = image.copy()
    for i, corner in enumerate(corners):
        x, y = int(corner[0]), int(corner[1])
        # Draw circles at corners
        cv2.circle(output, (x, y), radius, (0, 255, 0), -1)
        # Add corner numbers
        cv2.putText(output, str(i+1), (x+15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    # Draw boundary lines
    cv2.polylines(output, [corners.astype(np.int32)], True, (0, 255, 0), 3)
    return output

def create_download_link(image, filename, format_type):
    """
    Convert image to bytes for download
    Returns: (file_data, mime_type)
    """
    buffered = io.BytesIO()
    
    # Convert to PIL Image
    if len(image.shape) == 2:  # Grayscale
        pil_img = Image.fromarray(image)
    else:  # Color
        pil_img = Image.fromarray(image)
    
    # Save in requested format
    if format_type == "PDF":
        pil_img.save(buffered, format="PDF")
        mime_type = "application/pdf"
    elif format_type == "PNG":
        pil_img.save(buffered, format="PNG")
        mime_type = "image/png"
    else:  # JPG
        if len(image.shape) == 2:
            pil_img = pil_img.convert('RGB')
        pil_img.save(buffered, format="JPEG", quality=95)
        mime_type = "image/jpeg"
    
    return buffered.getvalue(), mime_type

# ============================================================================
# STREAMLIT APPLICATION
# ============================================================================

def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(page_title="📄 Document Scanner", layout="wide")
    st.title("📄 Smart Document Scanner")
    st.write("Upload a document image to automatically detect, transform, and export as a clean scanned copy")
    
    # Initialize session state
    if 'corners' not in st.session_state:
        st.session_state.corners = None
    if 'image' not in st.session_state:
        st.session_state.image = None
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Scan Mode")
        scan_mode = st.radio(
            "Choose processing style:",
            ["Black & White", "Enhanced B&W"],
            help="Black & White: Clean text | Enhanced B&W: Better for backgrounds",
            label_visibility="collapsed")
        
        st.divider()
        
        st.subheader("🔧 Adjustments")
        noise_reduction = st.slider(
            "Noise Reduction",
            min_value=0,
            max_value=5,
            value=2,
            help="Higher values remove more noise but may lose detail")
        
        st.divider()
        st.info("💡 Tip: Use 'Black & White' for text documents and 'Enhanced B&W' for documents with backgrounds")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Document Image", type=Config.SUPPORTED_FORMATS)
    
    if uploaded_file is not None:
        # Load image
        image = np.array(Image.open(uploaded_file))
        st.session_state.image = image
        
        # Auto-detect corners on first load
        if st.session_state.corners is None:
            doc_contour, edges = detect_document_contour(image)
            if doc_contour is not None:
                st.session_state.corners = doc_contour.reshape(4, 2)
            else:
                # Fallback: use image corners if detection fails
                h, w = image.shape[:2]
                st.session_state.corners = np.array([
                    [w*0.1, h*0.1],
                    [w*0.9, h*0.1],
                    [w*0.9, h*0.9],
                    [w*0.1, h*0.9]
                ], dtype=np.float32)
        
        # Display columns with aligned headers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Original Document")
        
        with col2:
            st.subheader("📄 Scanned Result")
        
        # Display images in aligned columns
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.corners is not None:
                display_img = draw_corners(image, st.session_state.corners)
                st.image(display_img, width="stretch")
            else:
                st.image(image, width="stretch")
                st.error("❌ No document detected. Try a clearer image with visible edges.")
        
        with col2:
            if st.session_state.corners is not None:
                # Apply perspective transformation
                warped = four_point_transform(image, st.session_state.corners)
                
                # Apply selected scan mode
                scanned = apply_scan_mode(warped, scan_mode, noise_reduction)
                st.session_state.processed_image = scanned
                
                # Display scanned image
                st.image(scanned, width="stretch", clamp=True)
            else:
                st.warning("⚠️ Please upload a clearer image with visible edges")
        
        # Export and Reset buttons below both images (aligned)
        if st.session_state.processed_image is not None:
            st.divider()
            
            action_col1, action_col2, action_col3 = st.columns([2, 1, 1])
            
            with action_col1:
                st.success("✅ Document scanned successfully!")
            
            with action_col2:
                # Export button
                export_clicked = st.button("📤 Export Document", width="stretch", type="primary")
            
            with action_col3:
                if st.button("🔄 Reset Corners", width="stretch"):
                    st.session_state.corners = None
                    st.session_state.processed_image = None
                    st.rerun()
            
            # Show format selection when export is clicked
            if export_clicked:
                st.info("📦 Choose your export format:")
                format_col1, format_col2, format_col3 = st.columns(3)
                
                with format_col1:
                    file_data_jpg, mime_jpg = create_download_link(
                        st.session_state.processed_image, "scanned_doc.jpg", "JPG")
                    st.download_button(
                        label="📄 JPG",
                        data=file_data_jpg,
                        file_name="scanned_document.jpg",
                        mime=mime_jpg,
                        width="stretch")
                
                with format_col2:
                    file_data_png, mime_png = create_download_link(
                        st.session_state.processed_image, "scanned_doc.png", "PNG")
                    st.download_button(
                        label="🖼️ PNG",
                        data=file_data_png,
                        file_name="scanned_document.png",
                        mime=mime_png,
                        width="stretch")
                
                with format_col3:
                    file_data_pdf, mime_pdf = create_download_link(
                        st.session_state.processed_image, "scanned_doc.pdf", "PDF")
                    st.download_button(
                        label="📑 PDF",
                        data=file_data_pdf,
                        file_name="scanned_document.pdf",
                        mime=mime_pdf,
                        width="stretch")
    
    else:
        # Show instructions when no file is uploaded
        with st.expander("📖 Quick Guide"):
            st.markdown("""
            **How to use:**
            1. Upload a document photo
            2. Auto-detection finds document boundaries (green lines)
            3. Choose scan mode: **Black & White** for text, **Enhanced B&W** for backgrounds
            4. Adjust noise reduction if needed (0-5)
            5. Click **Export** to download in JPG, PNG, or PDF
            
            **Tips:**
            - Ensure good lighting and visible document edges
            - Use the **Reset** button if wrong corners are detected
            - Higher noise reduction = cleaner but may lose fine details
            """)

if __name__ == "__main__":
    main()