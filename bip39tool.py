try:
    import itertools
    import time
    import os
    import sys
    from bip_utils import (
        Bip39MnemonicValidator,
        Bip39Languages,
        Bip39SeedGenerator,
        Bip44,
        Bip44Coins
    )
    from termcolor import cprint

    print("🔁 Запуск перебора слов...")

    # === ТВОИ ДАННЫЕ ===
    TARGET_ADDRESS = ""

    # Частично известная мнемоника (пример 12 слов)
    partial_mnemonic = [
        None, None, None, None,
        None, None, None, None,
        None, None, None, None
    ]

    # === ЗАГРУЗКА СЛОВАРЯ BIP39 ===
    try:
        with open("bip39_english.txt", "r", encoding="utf-8") as f:
            bip39_words = [word.strip() for word in f.readlines()]
    except FileNotFoundError:
        print("❌ Ошибка: файл bip39_english.txt не найден!")
        exit(1)

    if len(bip39_words) != 2048:
        print(f"❌ Ошибка: неправильное количество слов в словаре ({len(bip39_words)} вместо 2048)")
        exit(1)

    # Индексы неизвестных слов
    missing_indexes = [i for i, word in enumerate(partial_mnemonic) if word is None]

    if not missing_indexes:
        print("ℹ️ Все слова заданы, нечего перебирать.")
        exit(0)

    print(f"📌 Неизвестных слов: {len(missing_indexes)}")
    print(f"💡 Всего комбинаций: {len(bip39_words) ** len(missing_indexes)}")

    counter = 0
    valid_counter = 0
    invalid_counter = 0
    start_time = time.time()

    # === ПЕРЕБОР ВСЕХ КОМБИНАЦИЙ ===
    for combo in itertools.product(bip39_words, repeat=len(missing_indexes)):
        mnemonic = partial_mnemonic[:]
        for idx, word in zip(missing_indexes, combo):
            mnemonic[idx] = word

        phrase = " ".join(mnemonic)

        # Показываем процесс подбора
        print(f"\r[Пробую {counter}] {phrase}", end="", flush=True)

        try:
            # Проверка валидности фразы c ЯВНЫМ указанием языка
            validator = Bip39MnemonicValidator(lang=Bip39Languages.ENGLISH)
            if not validator.IsValid(phrase):
                invalid_counter += 1
                continue

            valid_counter += 1

            # Генерация seed и получение адреса
            seed_bytes = Bip39SeedGenerator(phrase, lang=Bip39Languages.ENGLISH).Generate()
            wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
            address = wallet.PublicKey().ToAddress()

            counter += 1
            print(f"\n[{counter}] {address} ← {phrase}")

            if address == TARGET_ADDRESS:
                cprint("\n✅ Найдено совпадение!", "green", attrs=["bold"])
                cprint("Сид-фраза:", "green")
                for i, word in enumerate(mnemonic):
                    color = "green" if partial_mnemonic[i] == word else "cyan"
                    cprint(f"{i+1:2d}. {word}", color)
                with open("found.txt", "w", encoding="utf-8") as f:
                    f.write(phrase + "\n")
                break

        except Exception as e:
            print(f"\n⚠️ Ошибка генерации для фразы: {phrase}\n{e}")
            continue

    elapsed_time = time.time() - start_time
    print(f"\n⏱️ Завершено за {elapsed_time:.2f} сек.")
    print(f"🔵 Проверено валидных фраз: {valid_counter}")
    print(f"🔴 Пропущено невалидных фраз: {invalid_counter}")

except Exception as global_error:
    print(f"\n❗ Ошибка при выполнении программы: {global_error}")
