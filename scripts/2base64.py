import base64

image_path = "../test.png"

def main():
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    print(image_base64)

if __name__ == "__main__":
    main()