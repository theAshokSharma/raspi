https://github.com/PyImageSearch/imutils



#### https://qengineering.eu/install-gstreamer-1.18-on-raspberry-pi-4.html
### Using gstreamer on Raspberrypi
#### additional plugins you must install before you can stream live video. 
#### For those familiar with the previous 1.14.4 version of Buster, it's almost the same list of libraries. 
#### Please, follow the commands below.
#### install a missing dependency
```
sudo apt-get install libx264-dev libjpeg-dev
```
#### install the remaining plugins
```
sudo apt-get install libgstreamer1.0-dev \
     libgstreamer-plugins-base1.0-dev \
     libgstreamer-plugins-bad1.0-dev \
     gstreamer1.0-plugins-ugly \
     gstreamer1.0-tools \
     gstreamer1.0-gl \
     gstreamer1.0-gtk3
```
#### if you have Qt5 install this plugin
```
sudo apt-get install gstreamer1.0-qt5
```
#### install if you want to work with audio
```
sudo apt-get install gstreamer1.0-pulseaudio
```

#### test streaming
```
gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink


gst-launch-1.0 libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! videoscale ! clockoverlay time-format="%D %H:%M:%S" ! autovideosink

```

Streaming to screen.
The first example is a simple streaming to the screen. You have seen it already working in the above sections. Note the scaling at the end of the pipeline.

```
gst-launch-1.0 v4l2src device=libcamerasrc ! video/x-raw, width=1280, height=720, framerate=30/1 ! videoconvert ! videoscale ! clockoverlay time-format="%D %H:%M:%S" ! video/x-raw, width=640, height=360 ! autovideosink
```

Streaming to OpenCV.
The following example is streaming to your OpenCV application. The best practice is by using raw images instead of motion compressed streams like mp4. The sink is now called appsink. The pipeline is encapsulated in a single routine. We show you a snippet of code, more on our GitHub page.

```
    #include <opencv2/opencv.hpp>

    std::string gstreamer_pipeline(int device, int capture_width, int capture_height, int framerate, int display_width, int display_height) {
        return
                " v4l2src device=/dev/video"+ std::to_string(device) + " !"
                " video/x-raw,"
                " width=(int)" + std::to_string(capture_width) + ","
                " height=(int)" + std::to_string(capture_height) + ","
                " framerate=(fraction)" + std::to_string(framerate) +"/1 !"
                " videoconvert ! videoscale !"
                " video/x-raw,"
                " width=(int)" + std::to_string(display_width) + ","
                " height=(int)" + std::to_string(display_height) + " ! appsink";
    }
    ////////////
    int main()
    {
        //pipeline parameters
        int capture_width = 1280 ;
        int capture_height = 720 ;
        int display_width = 640 ;
        int display_height = 360 ;
        int framerate = 30 ;

        std::string pipeline = gstreamer_pipeline(0,capture_width, capture_height,
                                                display_width, display_height, framerate);

        cv::VideoCapture cap(pipeline, cv::CAP_GSTREAMER);
        if(!cap.isOpened()) {
            std::cout << "Failed to open camera." << std::endl;
            return (-1);
        }
```
Deep learning applications have long inference times. In most cases, the processing time of a frame takes longer than the framerate of the stream. You get out of of sync, resulting in an increasing lag between reality and the captured images.
There are two possible solutions to this problem.
You could continuously grab images in a separate thread.
Or determine the missed images and skip them before grabbing a new frame. The latter solution is implemented in our RTSP-with-OpenCV repo.
In fact, it is much more than just RTSP streaming. You can use any resource, as the code snippet below shows.


#### UDP streaming.
For completeness, the UDP streamer again. The port number (5200) is arbitrary. You can choose any number you want, preferably over 1000, as long as the sender and receiver use the same number.


```
get the IP address of the recieving RPi first
hostname -I
# start the sender, the one with the Raspicam
gst-launch-1.0 -v v4l2src device=libcamerasrc num-buffers=-1 ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! jpegenc ! rtpjpegpay ! udpsink host=192.168.178.84 port=5200
```

start the reciever, the one with IP 192.168.178.84
```
gst-launch-1.0 -v udpsrc port=5200 ! application/x-rtp, media=video, clock-rate=90000, payload=96 ! rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink
```


#### TCP streaming.
And the TCP streamer once more. Same as with UDP, you can choose any port you like.

```
# get the IP address of the sending RPi first
hostname -I
# start the sender, the one with the Raspicam and IP 192.168.178.32
gst-launch-1.0 -v v4l2src device=libcamerasrc num-buffers=-1 ! video/x-raw,width=640,height=480, framerate=30/1 ! videoconvert ! jpegenc ! tcpserversink  host=192.168.178.32 port=5000
# start the reciever and connect to the server with IP 192.168.178.32
gst-launch-1.0 tcpclientsrc host=192.168.178.32 port=5000 ! jpegdec ! videoconvert ! autovideosink
```

#### RTSP streaming.
RTSP streaming is widespread. It is designed to control media streaming sessions between endpoints. In contrast to the single client connection of TCP and UDP, RTSP can connect a single server to multiple clients. In practice, the number of clients will be limited by the bandwidth capacity of a Raspberry Pi.
Before you can start streaming RTSP, you need the gst-rtsp-server and its examples. See the installation instructions in the section of your GStreamer version 1.14.4, or 1.18.4. As you can see, the pipeline assumes that your source is capable of the x-h264 format, like the raspicam. If not, you need to convert the format.

```
# select the proper folder
cd ~/gst-rtsp-server-1.18.4/build/examples

Showstopper.
Given the many questions on the forums, getting RTSP working under Bullseye is not that easy.
The pipeline below should work (?) If not, go back to Buster or use the old camera stack V4L2.
# run the pipeline

./test-launch "libcamerasrc ! video/x-h264, width=640, height=480, framerate=30/1 ! h264parse config-interval=1 ! rtph264pay name=pay0 pt=96"
```