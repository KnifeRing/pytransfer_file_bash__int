import paramiko
import os
import getpass

def transfer_file_scp(local_path, remote_path, host, user, password):
    try:
        # Создание SSH-клиента
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключение к удаленному компьютеру (порт всегда 22)
        ssh.connect(host, port=22, username=user, password=password)

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

            target_dir = f"/home/{user}/Desktop/_cardtest"
            print(f"Переход в директорию {target_dir}...")

            # Выполнение команд поочередно
            commands = [
                "sudo chmod +x *",  # Даем права на выполнение всем файлам в директории
                "sudo bash cardtest.sh",  # Запуск скрипта cardtest.sh
                "sudo bash test.sh"  # Запуск скрипта test.sh
            ]

            for command in commands:
                print(f"Выполнение команды: {command}")
                stdin, stdout, stderr = ssh.exec_command(f"cd {target_dir} && {command}")
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
        transfer_file_scp(local_path, remote_path, host, user, password)

    # Ожидание ввода перед закрытием
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()