import os
import sys


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_menu():
    clear()
    print("=" * 50)
    print("       🐍 SNAKE DEEP Q-LEARNING")
    print("=" * 50)
    print("1. 🎮  Play Game (Human)")
    print("2. 🤖  Train AI Agent")
    print("3. 👀  Watch AI Play")
    print("4. ❌  Exit")
    print("=" * 50)


def main():
    while True:
        print_menu()
        choice = input("Chọn chế độ (1-4): ").strip()

        if choice == "1":
            from play_human import play
            play()

        elif choice == "2":
            from train_ai import train
            print("\n[Enter] để train từ đầu")
            path = input("Nhập đường dẫn model cũ (optional): ").strip()
            train(resume_model=path if path else None)

        elif choice == "3":
            from watch_ai import watch
            print("\n[Enter] để dùng model tốt nhất")
            path = input("Nhập đường dẫn model (optional): ").strip()
            watch(path if path else "checkpoints/model_best.pth")

        elif choice == "4":
            print("Tạm biệt!")
            sys.exit(0)

        else:
            input("Lựa chọn không hợp lệ. Nhấn Enter để thử lại...")


if __name__ == "__main__":
    main()