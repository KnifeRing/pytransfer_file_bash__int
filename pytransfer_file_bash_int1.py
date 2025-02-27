import paramiko
import os
import getpass

def transfer_file_scp(local_path, remote_path, host, port, user, password):
    try:
        # Создание SSH-клиента
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключение к удаленному компьютеру
        ssh.connect(host, port=port, username=user, password=password)

        # Использование SFTP для передачи файла
        sftp = ssh.open_sftp()

        # Проверка существования удаленной директории
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)  # Проверяем, существует ли директория
        except FileNotFoundError:
            print(f"Ошибка: Удаленная директория {remote_dir} не существует.")
            sftp.mkdir(remote_dir)  # Создаем директорию, если её нет
            print(f"Директория {remote_dir} создана.")

        # Передача файла
        sftp.put(local_path, remote_path)
        sftp.close()

        print(f"Файл {local_path} успешно передан на {user}@{host}:{remote_path}")

        # Если файл является ZIP-архивом, распаковываем его
        if remote_path.endswith(".zip"):
            print("Обнаружен ZIP-архив. Распаковываем...")
            # Распаковываем архив
            stdin, stdout, stderr = ssh.exec_command(f"unzip {remote_path} -d {remote_dir}")
            print("Результат распаковки:")
            print(stdout.read().decode())
            if stderr.read():
                print("Ошибки распаковки:")
                print(stderr.read().decode())

        # Выполнение команд на удаленном сервере
        while True:
            command = input("Введите команду для выполнения на удаленном сервере (или 'exit' для выхода): ")
            if command.lower() == 'exit':
                break
            stdin, stdout, stderr = ssh.exec_command(command)
            print("Результат выполнения команды:")
            print(stdout.read().decode())
            if stderr.read():
                print("Ошибки выполнения команды:")
                print(stderr.read().decode())

    except Exception as e:
        print(f"Ошибка при передаче файла: {e}")
    finally:
        # Закрытие соединения
        if 'ssh' in locals():
            ssh.close()

def main():
    # Запрашиваем данные у пользователя
    local_path = input("Введите локальный путь к файлу: ")  # Локальный файл
    host = input("Введите IP-адрес или имя хоста удаленного компьютера: ")  # Хост
    port = int(input("Введите порт SSH (по умолчанию 22): ") or 22)  # Порт (по умолчанию 22)
    user = input("Введите имя пользователя на удаленном компьютере: ")  # Пользователь
    password = getpass.getpass("Введите пароль пользователя: ")  # Пароль (скрытый ввод)

    # Проверка существования локального файла
    if not os.path.exists(local_path):
        print(f"Ошибка: Локальный файл {local_path} не существует.")
    else:
        # Формирование удаленного пути
        file_name = os.path.basename(local_path)  # Имя файла из локального пути
        remote_path = f"/home/{user}/Desktop/{file_name}"  # Удаленный путь с сохранением имени и формата

        # Передача файла
        transfer_file_scp(local_path, remote_path, host, port, user, password)

    # Ожидание ввода перед закрытием
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()