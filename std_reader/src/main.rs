use std::fs;
use std::io::{self, BufRead};
use std::process;

fn ls() -> Result<Vec<String>, io::Error> {
    // Чтение содержимого указанной директории
    let entries = fs::read_dir("/home/pc/auto_start_protacol/std")?;
    
    // Создание вектора для хранения имен файлов
    let mut file_list: Vec<String> = Vec::new();

    for entry in entries {
        let entry = entry?;
        let path = entry.path(); // Получаем путь текущего элемента
        
        // Попробуем открыть файл
        match fs::File::open(&path) {
            // Преобразуем Path в строку и добавляем в список
            Ok(_) => {
                if let Some(file_name) = path.file_name() {
                    file_list.push(file_name.to_string_lossy().into_owned());
                }
            },
            Err(err) => println!("Ошибка при открытии файла {:?}: {}", path, err),
        }  
    }

    // Выводим список открытых файлов
    println!("Открытые файлы:\n");
    for (index, file) in file_list.iter().enumerate() {
        println!("{}: {}", index, file);
    }
    
    Ok(file_list) // Возвращаем список файлов
}

fn main(){
    // Получаем список файлов
    let file_list = ls();

    match file_list {
        Ok(files) => {
            println!("Введите индекс файла для чтения: ");
            loop {
                let mut input = String::new();
                
                io::stdin().read_line(&mut input).expect("Не удалось прочитать строку");
                print!(">");
                if input.trim() == "q"{process::exit(0)}

                if input.trim() == "menu"{
                    process::Command::new("clear").status().unwrap();
                    let _ = ls();
                }
                // Преобразуем ввод в usize
                match input.trim().parse::<usize>() {
                    Ok(index) => {
                        // Проверяем, существует ли элемент по указанному индексу
                        if let Some(file_name) = files.get(index) {
                            // Полный путь к файлу. Замените на свой путь.
                            let full_path = format!("/home/pc/auto_start_protacol/std/{}", file_name);
                            
                            // Отрываем файл и читаем содержимое
                            let file = fs::File::open(&full_path);
                            match file {
                                Ok(file) => {
                                    let reader = io::BufReader::new(file);
                                    for line in reader.lines() {
                                        match line {
                                            Ok(content) => println!("{}", content),
                                            Err(err) => println!("Ошибка: {}", err),
                                        }
                                    }
                                },
                                Err(err) => {println!("Ошибка: {}", err)},
                            }
                            
                        } else {
                            println!("Файл с индексом {} не найден.", index);
                        }
                    },
                    Err(_) => println!("Пожалуйста, введите корректный индекс."),
                }
            }
        },
        Err(err) => println!("Ошибка: {}", err),
    }
}
