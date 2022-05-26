from serial.tools.list_ports import comports


def main():
    for port in comports():
        print(f"{port.name}: {port.hwid}")


if __name__ == "__main__":
    main()
