"""
Camera Permission Test Script
==============================
Tests camera access and helps diagnose permission issues.

Run: python test_camera.py
"""

import cv2
import sys
import platform


def test_camera(camera_index=0):
    """Test camera access and permissions."""
    
    print("="*60)
    print("Camera Permission Test")
    print("="*60)
    print(f"\nSystem: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"OpenCV: {cv2.__version__}")
    print()
    
    # Test different camera indices
    print(f"Testing camera index {camera_index}...")
    
    try:
        # Try to open camera
        camera = cv2.VideoCapture(camera_index)
        
        if not camera.isOpened():
            print(f"❌ FAILED: Cannot open camera {camera_index}")
            print("\n💡 Troubleshooting steps:")
            print("   1. Check if camera is connected")
            print("   2. Close other apps using camera (Zoom, Skype, etc.)")
            print("   3. Check camera permissions in system settings")
            print("   4. Try different camera index (0, 1, 2)")
            
            if platform.system() == "Darwin":  # macOS
                print("\n   macOS: Go to System Preferences → Security & Privacy")
                print("          → Camera → Enable for Terminal/Python")
            
            elif platform.system() == "Windows":
                print("\n   Windows: Settings → Privacy → Camera")
                print("            → Enable 'Camera access' and 'Desktop apps'")
            
            elif platform.system() == "Linux":
                print("\n   Linux: Run 'sudo usermod -a -G video $USER'")
                print("          Then log out and log back in")
            
            return False
        
        # Try to read a frame
        ret, frame = camera.read()
        
        if not ret or frame is None:
            print(f"❌ FAILED: Camera opened but cannot read frames")
            print("\n💡 Camera might be in use by another application")
            camera.release()
            return False
        
        # Success!
        print(f"✅ SUCCESS: Camera {camera_index} is working!")
        print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
        print(f"   Channels: {frame.shape[2]}")
        print()
        
        # Display test frame
        print("Opening camera preview window...")
        print("Press 'q' to close the preview")
        
        while True:
            ret, frame = camera.read()
            
            if not ret:
                break
            
            # Add text to frame
            cv2.putText(
                frame,
                "Camera Test - Press 'q' to quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.imshow('Camera Permission Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()
        
        print("\n✅ Camera test completed successfully!")
        print("   Your camera is working and has proper permissions.")
        print("\n🚀 You can now run: python gui.py")
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n💡 This might be a permission or driver issue")
        return False


def check_multiple_cameras():
    """Check for multiple cameras."""
    print("\n" + "="*60)
    print("Checking for available cameras...")
    print("="*60 + "\n")
    
    found_cameras = []
    
    for i in range(5):  # Check indices 0-4
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            ret, _ = camera.read()
            if ret:
                found_cameras.append(i)
                print(f"✓ Camera {i}: Available")
            else:
                print(f"⚠ Camera {i}: Detected but cannot read")
            camera.release()
        else:
            print(f"✗ Camera {i}: Not available")
    
    print()
    
    if found_cameras:
        print(f"Found {len(found_cameras)} working camera(s): {found_cameras}")
        return found_cameras[0]
    else:
        print("No working cameras found")
        return None


def main():
    """Main test function."""
    
    # Check for multiple cameras
    camera_index = check_multiple_cameras()
    
    if camera_index is not None:
        print(f"\nTesting camera {camera_index}...")
        test_camera(camera_index)
    else:
        print("\n❌ No cameras available!")
        print("\n💡 Please check:")
        print("   1. Camera is physically connected")
        print("   2. Camera drivers are installed")
        print("   3. No other apps are using the camera")
        print("   4. Camera permissions are granted")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
