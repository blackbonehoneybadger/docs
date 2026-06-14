# 🦡 Honey Badger: Кавказский Забег

2D pixel-art платформер на **Godot 4.3 / GDScript**. Мир 1 — Адыгея.
Три играбельных персонажа, враги, монеты, чекпоинт, мобильное управление.

Игра рассчитана на разрешение **480×270** (pixel-art, upscaled, Nearest filter),
портретную/ландшафтную мобильную сборку под **Android** и десктоп для разработки.

---

## Как открыть и запустить

1. Установите **Godot 4.3** (стандартная версия, GDScript).
2. В Godot нажмите **Import** → выберите файл
   `HoneyBadger_KavkazRun/project.godot` → **Import & Edit**.
3. Нажмите **F5** (Run Project).
   Главная сцена — `scenes/ui/MainMenu.tscn`.

> Сцены уже сгенерированы как `.tscn` файлы — игра запускается сразу,
> **без** обязательного запуска инструмента сборки. Скрипты строят все
> дочерние узлы (спрайты, коллизии, хитбоксы, тайлмап уровня) программно
> в `_ready()`, поэтому внешние ассеты не требуются.

### (Опционально) Перегенерировать спрайты и звуки

Спрайты рисуются в коде, а звук терпимо относится к отсутствующим файлам,
поэтому это не обязательно. Но если нужны PNG-спрайты и процедурные
звуки/музыка как файлы на диске:

1. Откройте в редакторе `build_all_scenes.gd`.
2. **File ▸ Run** (или кнопка Run в редакторе скриптов).
3. Скрипт создаст:
   - все `.tscn` сцены (перезапишет существующие — идентичны),
   - placeholder PNG-спрайты в `assets/characters/*` и `assets/ui/portraits/*`,
   - процедурные звуки `.wav` в `assets/audio/sfx/`,
   - 8-bit музыку `.wav` в `assets/audio/music/`.

---

## Управление

**Клавиатура (десктоп):**

| Действие     | Клавиши            |
|--------------|--------------------|
| Влево/вправо | A/D или ←/→        |
| Прыжок (A)   | Space / W / ↑      |
| Атака (B)    | Z / J              |
| Спецатака (S)| X / K              |
| Пауза        | Esc                |

**Сенсор (Android):** слева — виртуальный джойстик (тащить для движения),
справа — кнопки **A** (прыжок), **B** (атака), **S** (спецатака) и кнопка паузы
вверху справа. Поддерживается мультитач; на ПК работает через эмуляцию мыши.

---

## Персонажи

| Персонаж     | Роль    | Скорость | Прыжок | HP | Атака / особенность                        |
|--------------|---------|----------|--------|----|--------------------------------------------|
| Honey Badger | Герой   | 180      | 360    | 3  | Ядовитая катана — враг тает в зелёном дыму |
| Boy          | Танк    | 130      | 280    | 5  | Удар по земле (радиус 96px), ломает камень |
| Mr. Kroo     | Ловкач  | 220      | 430    | 2  | Ножницы — враги разлетаются конфетти        |

Общая механика: гравитация 980, coyote time 0.12с, jump buffer 0.10с,
неуязвимость 1.5с с миганием, прыжок на голову врага (stomp) убивает,
смерть при падении ниже y=900.

## Враги (Мир 1)

- **Forest Spirit** — летает по синусоиде, преследует игрока < 200px, HP 1.
- **Stone Snail** — медленный патруль (40), HP 2 (первый удар → панцирь 2с).
- **Cave Bat** — горизонтальный синус, пикирует на игрока, HP 1.

Враги разворачиваются у края платформы и у стены (RayCast2D), получают
knockback, дают +200 очков. Эффекты мультяшные, без реалистичной крови.

---

## Структура проекта

```
HoneyBadger_KavkazRun/
├── project.godot              # настройки, autoload, input map
├── build_all_scenes.gd        # инструмент: генерация сцен/спрайтов/звуков
├── icon.svg
├── assets/                    # сгенерированные спрайты, портреты, звук, конфиг
│   └── characters/shared/characters_config.json
├── scenes/                    # .tscn (ui, characters, enemies, objects, levels)
└── scripts/
    ├── globals/   GameManager, CharacterConfig, AudioManager, PixelArt
    ├── characters/ BaseCharacter + HoneyBadger / Boy / MrKroo
    ├── enemies/    BaseEnemy + ForestSpirit / StoneSnail / CaveBat
    ├── objects/    Coin, Checkpoint, LevelEnd, StoneBlock
    ├── ui/         MainMenu, CharacterSelect, HUD, PauseMenu, GameOver,
    │               LevelComplete, MobileControls
    └── levels/     Level01_01, LevelGenerator
```

### Autoload-сервисы

- **GameManager** — состояние: выбранный персонаж, жизни, монеты, счёт,
  рекорд; `add_coin()`, `lose_life()`, `level_complete()`,
  `get_character_scene_path()`. Также гарантирует наличие input-действий.
- **CharacterConfig** — грузит `characters_config.json` с fallback на
  встроенные данные; `get_character(id)`, `get_stat(id, stat)`.
- **AudioManager** — `play_music(path, loop)`, `play_sfx(name_or_path)`,
  `set_music_volume(v)`, `set_sfx_volume(v)`.

---

## Сборка под Android (APK)

1. В Godot: **Editor ▸ Manage Export Templates** → скачать шаблоны 4.3.
2. Установить **Android SDK** и указать путь в
   **Editor ▸ Editor Settings ▸ Export ▸ Android**.
3. **Project ▸ Export ▸ Add… ▸ Android**, настроить package name и keystore.
4. **Export Project** → `.apk` (или `.aab` для Google Play).

Рендер выставлен в `gl_compatibility` (OpenGL ES 3) для совместимости с
мобильными устройствами; ориентация — landscape.

---

## Расширение на новые миры

Уровень собирается кодом в `LevelGenerator.gd`. Чтобы добавить мир/уровень:
создайте новый генератор (или параметризуйте текущий) и новую сцену-уровень
по образцу `scenes/levels/world_01_adygea/Level_01_01.tscn` +
`scripts/levels/Level01_01.gd`. Враги, монеты и объекты — самодостаточные
скрипты, их легко переиспользовать.
