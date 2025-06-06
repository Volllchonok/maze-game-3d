from core.game import Game


def main():
    """Головна функція"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nГру зупинено користувачем")
    except Exception as e:
        print(f"Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()