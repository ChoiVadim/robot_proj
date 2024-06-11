import cv2
import serial


def connect_to_arduino(port, baud_rate=9600, simulate=False):
    # Connect to Arduino via serial port, or simulate
    if simulate:
        return None
    try:
        return serial.Serial(port, baud_rate)
    except serial.SerialException as e:
        print(f"Failed to connect on {port}: {e}")
        exit(1)


def send_command(ser, command):
    # Send a command to Arduino, or simulate
    if ser is None:
        print(f"Simulated command: {command}")
        return
    try:
        ser.write((command + "\n").encode())
        print(f"Sent '{command}' to Arduino")
    except serial.SerialException as e:
        print(f"Error sending data: {e}")
        exit(1)


# QR code value
target_qr_code = "https://example.com"
cv2_reader = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)

try:
    ser = connect_to_arduino(port="/dev/ttyUSB0", baud_rate=9600, simulate=True)

    prev_time = cv2.getTickCount()
    fps = 0
    max_fps = 0
    count = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # frame = cv2.resize(frame, (320, 240))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)

        try:
            # Detect and decode the QR code in the frame
            cv2_out, cord, _ = cv2_reader.detectAndDecode(frame)
            if cv2_out == target_qr_code:
                cord = cord.tolist()[0]
                top_left = cord[0]
                top_right = cord[1]
                bottom_right = cord[2]
                bottom_left = cord[3]

                top_left = (int(top_left[0]), int(top_left[1]))
                bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

                mid_x = int((top_left[0] + bottom_right[0]) / 2)
                mid_y = int((top_left[1] + bottom_right[1]) / 2)
                area = abs(
                    (bottom_right[0] - top_left[0]) * (bottom_right[1] - top_left[1])
                )
                print(area)
                print(mid_x, mid_y)

                # Send movement commands based on area and position
                if area < 30000:

                    if mid_x < 250:
                        send_command(ser, "left")
                    elif mid_x > 400:
                        send_command(ser, "right")
                    else:
                        send_command(ser, "forward")
                else:
                    send_command(ser, "stop")

            else:
                count += 1
                if count > 3:
                    send_command(ser, "stop")
                    count = 0

                # Draw circle at midpoint and rectangle around QR code
                cv2.circle(frame, (mid_x, mid_y), 5, (0, 0, 255), 5)
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        except Exception as e:
            print(f"Error decoding QR code: {e}")
            pass

        # Calculate FPS
        current_time = cv2.getTickCount()
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()
        fps = 1 / time_diff
        prev_time = current_time

        # Display FPS on frame
        cv2.putText(
            frame,
            f"FPS: {fps:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2,
        )

        if fps > max_fps:
            max_fps = fps

        # Display the resulting frame
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            send_command(ser, "stop")
            break

finally:
    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
