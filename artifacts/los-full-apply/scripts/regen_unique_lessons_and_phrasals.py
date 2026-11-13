#!/usr/bin/env python3
"""Regenerate unique section-lesson dialogues + sync high-freq phrasals into bank."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "EnglishOnSite" / "Resources"


def L(en: str, ru: str, role: str, practice: bool = False, tip_ru: str | None = None) -> dict:
    return {"en": en, "ru": ru, "role": role, "tip_ru": tip_ru, "practice": practice}


def S(*pairs: tuple[str, str]) -> list[dict]:
    return [{"en": a, "ru": b} for a, b in pairs]


def script(scene: str, lines: list[dict], say: list[dict]) -> tuple[str, list[dict], list[dict]]:
    return scene, lines, say


# --- Onsite: 12 unique scripts per section (order matches lesson 01..12) ---

ONSITE: dict[str, list[tuple[str, list[dict], list[dict]]]] = {
    "construction": [
        script(
            "Утренний брифинг: план на день.",
            [
                L("Morning. What's the plan for today?", "Доброе утро. Какой план на сегодня?", "electrician", True),
                L("We start on the ground floor slab.", "Начинаем с плиты на первом этаже.", "foreman"),
                L("Do we need barriers up first?", "Сначала поставить ограждения?", "electrician", True),
                L("Yes. Put the barriers around the open edge.", "Да. Поставь ограждения вокруг открытого края.", "foreman", tip_ru="put the barriers"),
                L("OK, I'll set them now.", "Ок, сейчас поставлю.", "electrician", True),
                L("Good. Then wait for the pour team.", "Хорошо. Потом жди бригаду заливки.", "foreman"),
            ],
            S(("What's the plan for today?", "Какой план на сегодня?"), ("I'll set them now.", "Сейчас поставлю.")),
        ),
        script(
            "Подъём материалов — куда нести.",
            [
                L("Where do these bags go?", "Куда эти мешки?", "electrician", True),
                L("Take them to bay three.", "Отнеси их в отсек три.", "foreman", tip_ru="bay three"),
                L("Is the hoist free?", "Подъёмник свободен?", "electrician", True),
                L("Use the hoist. Don't carry them up the stairs.", "Используй подъёмник. Не тащи по лестнице.", "foreman"),
                L("Got it. How many trips?", "Понял. Сколько ходок?", "electrician", True),
                L("Four trips should cover it.", "Четырёх ходок хватит.", "foreman"),
            ],
            S(("Where do these bags go?", "Куда эти мешки?"), ("Is the hoist free?", "Подъёмник свободен?")),
        ),
        script(
            "Опасная зона — нельзя заходить.",
            [
                L("Is this area closed?", "Эта зона закрыта?", "electrician", True),
                L("Yes. Live works behind that tape.", "Да. За лентой — работы под напряжением.", "foreman"),
                L("Who can go in?", "Кто может заходить?", "electrician", True),
                L("Only the authorised crew with permits.", "Только допущенная бригада с нарядами.", "foreman"),
                L("I'll stay outside then.", "Тогда останусь снаружи.", "electrician", True),
                L("Good. Keep clear until I call you.", "Хорошо. Не заходи, пока не позову.", "foreman"),
            ],
            S(("Is this area closed?", "Эта зона закрыта?"), ("I'll stay outside then.", "Тогда останусь снаружи.")),
        ),
        script(
            "Доступ к лотку — подмости.",
            [
                L("I need access to that cable tray.", "Мне нужен доступ к тому лотку.", "electrician", True),
                L("Use the podium steps, not the wooden ladder.", "Бери подмости, не деревянную лестницу.", "foreman"),
                L("Are the wheels locked?", "Колёса зафиксированы?", "electrician", True),
                L("Check the brakes before you climb.", "Проверь тормоза перед подъёмом.", "foreman"),
                L("Brakes are on. Climbing now.", "Тормоза включены. Поднимаюсь.", "electrician", True),
                L("Someone foot the base if it wobbles.", "Если шатается — пусть кто-то придержит основание.", "foreman"),
            ],
            S(("I need access to that cable tray.", "Мне нужен доступ к тому лотку."), ("Are the wheels locked?", "Колёса зафиксированы?")),
        ),
        script(
            "Поставка короба опаздывает.",
            [
                L("The trunking delivery is late.", "Поставка короба опаздывает.", "electrician", True),
                L("How late?", "Насколько?", "foreman"),
                L("They said after lunch, maybe three.", "Сказали после обеда, может в три.", "electrician", True),
                L("Call the supplier and get a firm time.", "Позвони поставщику и возьми точное время.", "foreman"),
                L("OK. Should I switch to another task?", "Ок. Переключиться на другую задачу?", "electrician", True),
                L("Yes — pull cable on level two meanwhile.", "Да — пока тяни кабель на втором уровне.", "foreman"),
            ],
            S(("The trunking delivery is late.", "Поставка короба опаздывает."), ("Should I switch to another task?", "Переключиться на другую задачу?")),
        ),
        script(
            "Ветер на крыше — стоп работы.",
            [
                L("Wind is picking up on the roof.", "На крыше усиливается ветер.", "electrician", True),
                L("What's the reading?", "Какие показания?", "foreman"),
                L("About forty kilometres an hour.", "Около сорока километров в час.", "electrician", True),
                L("Stop roof work. Tie down loose sheets.", "Стоп работы на крыше. Закрепите свободные листы.", "foreman"),
                L("We'll move inside to the plant room.", "Перейдём внутрь в венткамеру.", "electrician", True),
                L("Good call. Report when you're clear.", "Правильно. Сообщи, когда освободитесь.", "foreman"),
            ],
            S(("Wind is picking up on the roof.", "На крыше усиливается ветер."), ("We'll move inside.", "Перейдём внутрь.")),
        ),
        script(
            "Разметка перед сверлением.",
            [
                L("Can you check my marks before I drill?", "Проверишь разметку перед сверлением?", "electrician", True),
                L("Show me the centres.", "Покажи центры.", "foreman"),
                L("Two hundred mil from the corner, level.", "Двести миллиметров от угла, по уровню.", "electrician", True),
                L("Looks right. Scan for cables first.", "Похоже верно. Сначала просканируй на кабели.", "foreman"),
                L("Scanner is clear. Drilling now.", "Сканер чистый. Сверлю.", "electrician", True),
                L("Use dust extraction.", "Включи пылеудаление.", "foreman"),
            ],
            S(("Check my marks before I drill.", "Проверь разметку перед сверлением."), ("Scanner is clear.", "Сканер чистый.")),
        ),
        script(
            "Сантехники в том же стояке.",
            [
                L("Plumbers are in the same riser.", "Сантехники в том же стояке.", "electrician", True),
                L("Talk to their lead before you pull.", "Поговори с их бригадиром до протяжки.", "foreman"),
                L("They need one more hour for the pipe.", "Им нужен ещё час на трубу.", "electrician", True),
                L("Then wait. Don't fight for space.", "Тогда подожди. Не спорьте за место.", "foreman"),
                L("I'll prep terminations outside.", "Подготовлю оконцовки снаружи.", "electrician", True),
                L("Perfect. Keep the doorway clear.", "Отлично. Не загромождай проход.", "foreman"),
            ],
            S(("Plumbers are in the same riser.", "Сантехники в том же стояке."), ("I'll prep terminations outside.", "Подготовлю оконцовки снаружи.")),
        ),
        script(
            "Конец смены — уборка и передача.",
            [
                L("What do you need before we leave?", "Что нужно перед уходом?", "electrician", True),
                L("Sweep the area and lock the container.", "Подмети зону и закрой контейнер.", "foreman"),
                L("Tools are back on the board.", "Инструмент на месте на стенде.", "electrician", True),
                L("Sign the handover sheet for night shift.", "Подпиши передачу ночной смене.", "foreman"),
                L("Done. Anything left open?", "Готово. Что-то осталось открытым?", "electrician", True),
                L("No. See you tomorrow at seven.", "Нет. До завтра в семь.", "foreman"),
            ],
            S(("Tools are back on the board.", "Инструмент на месте."), ("Anything left open?", "Что-то осталось открытым?")),
        ),
        script(
            "Порез — аптечка и акт.",
            [
                L("I cut my hand on the metal edge.", "Порезал руку об металлический край.", "electrician", True),
                L("How bad is it?", "Насколько серьёзно?", "foreman"),
                L("It's bleeding but not deep.", "Кровит, но неглубоко.", "electrician", True),
                L("Go to the first aid point now.", "Сейчас иди в пункт первой помощи.", "foreman"),
                L("Should I fill an incident form?", "Заполнять акт об инциденте?", "electrician", True),
                L("Yes, after they bandage you.", "Да, после того как перевяжут.", "foreman"),
            ],
            S(("I cut my hand.", "Порезал руку."), ("Should I fill an incident form?", "Заполнять акт?")),
        ),
        script(
            "Клиент на площадке — коротко.",
            [
                L("The client is asking about the delay.", "Клиент спрашивает про задержку.", "electrician", True),
                L("Be honest and short.", "Говори честно и коротко.", "foreman"),
                L("We waited on materials; we restart after lunch.", "Ждали материалы; продолжим после обеда.", "electrician", True),
                L("Good. Don't promise a finish time yet.", "Хорошо. Пока не обещай время сдачи.", "foreman"),
                L("Understood. I'll walk them to the safe path.", "Понял. Проведу их безопасным путём.", "electrician", True),
                L("Thanks. Stay with them until they leave.", "Спасибо. Будь с ними, пока не уйдут.", "foreman"),
            ],
            S(("We waited on materials.", "Ждали материалы."), ("I'll walk them to the safe path.", "Проведу безопасным путём.")),
        ),
        script(
            "Ночной тихий режим у жилья.",
            [
                L("Neighbours complained about noise after ten.", "Соседи жаловались на шум после десяти.", "electrician", True),
                L("No angle grinders after ten then.", "После десяти без болгарок.", "foreman"),
                L("Can we still drill inside?", "Можно сверлить внутри?", "electrician", True),
                L("Only low noise tasks indoors.", "Только тихие задачи внутри.", "foreman"),
                L("We'll switch to labeling and testing.", "Переключимся на маркировку и тесты.", "electrician", True),
                L("Yes. Keep voices down near the street.", "Да. Говорите тише у улицы.", "foreman"),
            ],
            S(("No angle grinders after ten.", "После десяти без болгарок."), ("We'll switch to labeling.", "Переключимся на маркировку.")),
        ),
    ],
    "websites_cctv": [
        script(
            "Обход с заказчиком — точки камер.",
            [
                L("Where do you want the entrance camera?", "Куда поставить камеру на входе?", "technician", True),
                L("Above the door, covering the path in.", "Над дверью, чтобы видеть входной путь.", "client"),
                L("Do you need face detail or just movement?", "Нужны лица или только движение?", "technician", True),
                L("Faces at the door. Movement in the yard.", "Лица у двери. Движение во дворе.", "client"),
                L("I'll mark both positions on the plan.", "Отмечу обе точки на плане.", "technician", True),
                L("Send me the plan before you drill.", "Пришли план до сверления.", "client"),
            ],
            S(("Where do you want the entrance camera?", "Куда камеру на входе?"), ("Faces at the door.", "Лица у двери.")),
        ),
        script(
            "Питание камеры — PoE.",
            [
                L("Is this run on PoE?", "Эта линия на PoE?", "technician", True),
                L("Yes, from the switch in the office.", "Да, от свитча в офисе.", "client"),
                L("Cable length is about eighty metres.", "Длина кабеля около восьмидесяти метров.", "technician", True),
                L("That should be fine for PoE.", "Для PoE должно хватить.", "client"),
                L("I'll test voltage at the camera end.", "Проверю напряжение на конце у камеры.", "technician", True),
                L("Call me if it's low.", "Позвони, если будет низкое.", "client"),
            ],
            S(("Is this run on PoE?", "Эта линия на PoE?"), ("I'll test voltage at the camera end.", "Проверю напряжение у камеры.")),
        ),
        script(
            "Витая пара без заломов.",
            [
                L("Can I share the same tray as power?", "Можно в один лоток с силой?", "technician", True),
                L("Keep data separate if you can.", "Если можно — данные отдельно.", "client"),
                L("There's a spare data tray above.", "Сверху есть свободный лоток для данных.", "technician", True),
                L("Use that. Leave a service loop.", "Используй его. Оставь технологический запас.", "client"),
                L("Loop at both ends, labelled.", "Петля с обоих концов, с маркировкой.", "technician", True),
                L("Perfect.", "Отлично.", "client"),
            ],
            S(("Can I share the same tray as power?", "Можно в один лоток с силой?"), ("Leave a service loop.", "Оставь технологический запас.")),
        ),
        script(
            "NVR — пароль и удалёнка.",
            [
                L("The NVR is online. Need the admin password.", "NVR в сети. Нужен пароль админа.", "technician", True),
                L("I'll text it. Change it after setup.", "Пришлю в сообщении. Потом смени.", "client"),
                L("Do you want remote view on the phone?", "Нужен просмотр с телефона?", "technician", True),
                L("Yes, for me and the night manager.", "Да, мне и ночному менеджеру.", "client"),
                L("I'll create two user accounts.", "Создам две учётки.", "technician", True),
                L("No shared logins, please.", "Без общих логинов, пожалуйста.", "client"),
            ],
            S(("Need the admin password.", "Нужен пароль админа."), ("I'll create two user accounts.", "Создам две учётки.")),
        ),
        script(
            "Камера смотрит в стену.",
            [
                L("Camera three shows the wall, not the gate.", "Камера три смотрит в стену, не на ворота.", "technician", True),
                L("Can you aim it from the ladder?", "Наведёшь с лестницы?", "client"),
                L("Yes. Watch the live view and guide me.", "Да. Смотри лайв и направляй.", "technician", True),
                L("Left a bit… stop. Tilt down.", "Чуть влево… стоп. Ниже.", "client"),
                L("Gate is centred now.", "Ворота по центру.", "technician", True),
                L("Lock the bracket and tighten it.", "Зафиксируй кронштейн и затяни.", "client"),
            ],
            S(("Camera three shows the wall.", "Камера три смотрит в стену."), ("Gate is centred now.", "Ворота по центру.")),
        ),
        script(
            "Ночная засветка.",
            [
                L("At night the image is washed out.", "Ночью картинка засвечена.", "technician", True),
                L("Street light is opposite the lens.", "Фонарь напротив объектива.", "client"),
                L("I can enable WDR or move it slightly.", "Могу включить WDR или чуть сдвинуть.", "technician", True),
                L("Try WDR first.", "Сначала попробуй WDR.", "client"),
                L("Better. Faces are readable now.", "Лучше. Лица читаются.", "technician", True),
                L("Save the profile as Night.", "Сохрани профиль как Night.", "client"),
            ],
            S(("The image is washed out.", "Картинка засвечена."), ("Faces are readable now.", "Лица читаются.")),
        ),
        script(
            "Запись остановилась.",
            [
                L("Recording stopped on channel two.", "Запись остановилась на канале два.", "technician", True),
                L("Is the disk full?", "Диск полный?", "client"),
                L("Disk is healthy. Schedule was off.", "Диск в порядке. Расписание было выключено.", "technician", True),
                L("Turn continuous recording back on.", "Включи непрерывную запись снова.", "client"),
                L("Done. I'll check twenty-four hours later.", "Готово. Проверю через сутки.", "technician", True),
                L("Send me a screenshot of the timeline.", "Пришли скрин таймлайна.", "client"),
            ],
            S(("Recording stopped on channel two.", "Запись остановилась на канале два."), ("Schedule was off.", "Расписание было выключено.")),
        ),
        script(
            "Приложение не находит NVR.",
            [
                L("The app can't find the device.", "Приложение не находит устройство.", "technician", True),
                L("Are you on the site Wi‑Fi?", "Ты в Wi‑Fi объекта?", "client"),
                L("Yes. Scanning the QR on the NVR.", "Да. Сканирую QR на NVR.", "technician", True),
                L("Allow local network permission on the phone.", "Разреши доступ к локальной сети на телефоне.", "client"),
                L("It connected. Live view works.", "Подключилось. Лайв работает.", "technician", True),
                L("Add a bookmark named Main gate.", "Добавь закладку Main gate.", "client"),
            ],
            S(("The app can't find the device.", "Приложение не находит устройство."), ("Live view works.", "Лайв работает.")),
        ),
        script(
            "Кабель перерезали.",
            [
                L("Someone cut the cable to camera five.", "Кто-то перерезал кабель к камере пять.", "technician", True),
                L("Can you splice it or pull a new run?", "Сваришь или новую линию потянешь?", "client"),
                L("Better to pull a new run — it's crushed.", "Лучше новую — кабель раздавлен.", "technician", True),
                L("Do it today if you can.", "Сделай сегодня, если успеешь.", "client"),
                L("I'll use the spare conduit path.", "Пойду запасным путём в трубе.", "technician", True),
                L("Mark it so they don't cut it again.", "Пометь, чтобы снова не перерезали.", "client"),
            ],
            S(("Someone cut the cable.", "Кто-то перерезал кабель."), ("I'll use the spare conduit path.", "Пойду запасным путём.")),
        ),
        script(
            "Передача объекта.",
            [
                L("Handover pack is ready.", "Пакет передачи готов.", "technician", True),
                L("What's inside?", "Что внутри?", "client"),
                L("IP list, passwords, cable plan, and app guide.", "IP, пароли, план кабелей и гайд по приложению.", "technician", True),
                L("Change default passwords with me now.", "Давай сейчас сменим заводские пароли.", "client"),
                L("Done. Old defaults are disabled.", "Готово. Старые пароли отключены.", "technician", True),
                L("Sign here and we're closed out.", "Подпиши здесь — и закрываем.", "client"),
            ],
            S(("Handover pack is ready.", "Пакет передачи готов."), ("Old defaults are disabled.", "Старые пароли отключены.")),
        ),
        script(
            "Ложные тревоги по движению.",
            [
                L("We're getting false motion alerts.", "Идут ложные тревоги по движению.", "technician", True),
                L("When?", "Когда?", "client"),
                L("Every time trees move in the wind.", "Каждый раз, когда деревья качает ветром.", "technician", True),
                L("Raise the sensitivity threshold.", "Подними порог чувствительности.", "client"),
                L("I'll also mask the tree zone.", "Ещё замаскирую зону с деревьями.", "technician", True),
                L("Test it tonight and message me.", "Протестируй ночью и напиши.", "client"),
            ],
            S(("False motion alerts.", "Ложные тревоги по движению."), ("I'll mask the tree zone.", "Замаскирую зону с деревьями.")),
        ),
        script(
            "Ещё одна камера на склад.",
            [
                L("Client wants one more camera in the stock room.", "Клиент хочет ещё камеру на складе.", "technician", True),
                L("Have we got a free PoE port?", "Есть свободный PoE-порт?", "client"),
                L("Yes, port eight is free.", "Да, порт восемь свободен.", "technician", True),
                L("Add it to the NVR and name it Stock.", "Добавь в NVR и назови Stock.", "client"),
                L("Licensed and recording.", "Лицензия есть, запись идёт.", "technician", True),
                L("Update the site map too.", "Обнови и карту объекта.", "client"),
            ],
            S(("One more camera in the stock room.", "Ещё камера на складе."), ("Port eight is free.", "Порт восемь свободен.")),
        ),
    ],
}


def _pair(
    your: str,
    partner: str,
    turns: list[tuple[str, str, str, bool, str | None]],
) -> list[dict]:
    out = []
    for en, ru, who, practice, tip in turns:
        role = your if who == "you" else partner
        out.append(L(en, ru, role, practice, tip))
    return out


def build_induction() -> list:
    your, partner = "new_starter", "supervisor"
    rows = [
        (
            "Регистрация на induction.",
            [
                ("Hi, I'm here for the site induction.", "Здравствуйте, я на induction.", "you", True, None),
                ("Have you got your Safe Pass with you?", "Safe Pass с собой?", "them", False, None),
                ("Yes, here it is.", "Да, вот он.", "you", True, None),
                ("Sign in and take a seat in the meeting room.", "Отметьтесь и садитесь в переговорке.", "them", False, "sign in"),
                ("What time does it start?", "Во сколько начинается?", "you", True, None),
                ("In ten minutes. Phones on silent.", "Через десять минут. Телефоны на беззвучный.", "them", False, None),
            ],
            S(("I'm here for the site induction.", "Я на induction."), ("Sign in and take a seat.", "Отметьтесь и садитесь.")),
        ),
        (
            "PPE — что надеть.",
            [
                ("What PPE do I need on this site?", "Какие СИЗ нужны на этом объекте?", "you", True, None),
                ("Hard hat, hi‑vis, safety boots, and glasses.", "Каска, жилет, ботинки и очки.", "them", False, None),
                ("Are gloves mandatory everywhere?", "Перчатки обязательны везде?", "you", True, None),
                ("For cutting and handling materials, yes.", "При резке и переноске — да.", "them", False, None),
                ("I need a larger hi‑vis.", "Мне нужен жилет побольше.", "you", True, None),
                ("Store is next to the canteen.", "Склад рядом со столовой.", "them", False, None),
            ],
            S(("What PPE do I need?", "Какие СИЗ нужны?"), ("I need a larger hi‑vis.", "Нужен жилет побольше.")),
        ),
        (
            "Аварийные выходы.",
            [
                ("Where is the nearest fire exit?", "Где ближайший пожарный выход?", "you", True, None),
                ("Follow the green signs to the yard.", "По зелёным указателям во двор.", "them", False, None),
                ("Where do we assemble?", "Где точка сбора?", "you", True, None),
                ("Assembly point B by the gate.", "Точка B у ворот.", "them", False, None),
                ("Who do I report to after a drill?", "Кому докладывать после тренировки?", "you", True, None),
                ("Your supervisor with your name checked off.", "Своему супервайзеру — вас отметили в списке.", "them", False, None),
            ],
            S(("Where is the nearest fire exit?", "Где ближайший пожарный выход?"), ("Where do we assemble?", "Где точка сбора?")),
        ),
        (
            "Разрешения на работы.",
            [
                ("Do I need a permit for hot works?", "Нужен наряд на огневые работы?", "you", True, None),
                ("Yes. No grinding without a permit.", "Да. Без наряда не резать.", "them", False, None),
                ("Who signs it?", "Кто подписывает?", "you", True, None),
                ("The area owner and the fire watcher.", "Хозяин зоны и наблюдающий за огнём.", "them", False, None),
                ("I'll raise it before I start.", "Оформлю до начала.", "you", True, None),
                ("Keep a extinguisher within reach.", "Держи огнетушитель рядом.", "them", False, None),
            ],
            S(("Do I need a permit for hot works?", "Нужен наряд на огневые работы?"), ("I'll raise it before I start.", "Оформлю до начала.")),
        ),
        (
            "Изоляция / LOTO.",
            [
                ("Is this circuit isolated?", "Эта цепь изолирована?", "you", True, None),
                ("Show me your lock and tag first.", "Сначала покажи свой замок и бирку.", "them", False, None),
                ("My lock is on the isolator.", "Мой замок на разъединителе.", "you", True, None),
                ("Prove dead before you touch anything.", "Проверь отсутствие напряжения до касания.", "them", False, "prove dead"),
                ("Tester shows zero. Safe to proceed?", "Тестер ноль. Можно продолжать?", "you", True, None),
                ("Yes. Keep your lock on until you finish.", "Да. Не снимай замок, пока не закончишь.", "them", False, None),
            ],
            S(("Is this circuit isolated?", "Эта цепь изолирована?"), ("Prove dead before you touch anything.", "Проверь отсутствие напряжения.")),
        ),
        (
            "Сообщить об опасности.",
            [
                ("I saw an uncovered hole near the stairs.", "Увидел открытый проём у лестницы.", "you", True, None),
                ("Did you barricade it?", "Огородил?", "them", False, None),
                ("I put cones around it and came to tell you.", "Поставил конусы и пришёл сказать.", "you", True, None),
                ("Good. We'll get a proper cover on it.", "Хорошо. Поставим нормальное перекрытие.", "them", False, None),
                ("Should I write it in the hazard book?", "Записать в журнал опасностей?", "you", True, None),
                ("Yes, and take a photo.", "Да, и сделай фото.", "them", False, None),
            ],
            S(("I saw an uncovered hole.", "Увидел открытый проём."), ("Should I write it in the hazard book?", "Записать в журнал опасностей?")),
        ),
        (
            "Работа на высоте.",
            [
                ("Can I use a ladder for that light?", "Можно лестницу для того светильника?", "you", True, None),
                ("Only if it's tied and footed.", "Только если закреплена и придержана.", "them", False, None),
                ("The podium is free — better?", "Подмости свободны — лучше?", "you", True, None),
                ("Yes. Use the podium.", "Да. Бери подмости.", "them", False, None),
                ("Harness needed above two metres?", "Страховка нужна выше двух метров?", "you", True, None),
                ("Follow the site method statement.", "Смотри метод-стейтмент объекта.", "them", False, None),
            ],
            S(("Can I use a ladder?", "Можно лестницу?"), ("Use the podium.", "Бери подмости.")),
        ),
        (
            "Химия / SDS.",
            [
                ("Where are the safety data sheets?", "Где паспорта безопасности?", "you", True, None),
                ("Folder on the wall in the store.", "Папка на стене на складе.", "them", False, None),
                ("This solvent needs gloves and goggles.", "Для этого растворителя нужны перчатки и очки.", "you", True, None),
                ("Correct. Use it only with ventilation.", "Верно. Только с вентиляцией.", "them", False, None),
                ("Where do I dispose of the rags?", "Куда девать ветошь?", "you", True, None),
                ("Red bin for contaminated waste.", "Красный бак для загрязнённых отходов.", "them", False, None),
            ],
            S(("Where are the safety data sheets?", "Где паспорта безопасности?"), ("Where do I dispose of the rags?", "Куда девать ветошь?")),
        ),
        (
            "Первая помощь.",
            [
                ("Who is the first aider today?", "Кто сегодня оказывающий первую помощь?", "you", True, None),
                ("Maria on channel two.", "Мария на канале два.", "them", False, None),
                ("Where is the first aid kit?", "Где аптечка?", "you", True, None),
                ("In the welfare cabin, left shelf.", "В бытовке, левая полка.", "them", False, None),
                ("If someone collapses, what do I do first?", "Если кто-то упал — что первым делом?", "you", True, None),
                ("Make safe, call first aid, then site manager.", "Обезопась, вызови первую помощь, потом менеджера.", "them", False, None),
            ],
            S(("Who is the first aider today?", "Кто сегодня first aider?"), ("Where is the first aid kit?", "Где аптечка?")),
        ),
        (
            "Транспорт на площадке.",
            [
                ("Where can delivery vans park?", "Где могут парковаться доставки?", "you", True, None),
                ("Only in the marked bay by the compound.", "Только в размеченной зоне у компаунда.", "them", False, None),
                ("Is reversing without a banksman allowed?", "Сдача назад без сигнальщика можно?", "you", True, None),
                ("No. Always use a banksman.", "Нет. Всегда со сигнальщиком.", "them", False, None),
                ("I'll radio before the truck enters.", "Перед въездом грузовика вызову по рации.", "you", True, None),
                ("Good. Keep pedestrians clear.", "Хорошо. Пешеходов не подпускай.", "them", False, None),
            ],
            S(("Where can delivery vans park?", "Где парковать доставки?"), ("Always use a banksman.", "Всегда со сигнальщиком.")),
        ),
        (
            "Электричество — чужие щиты.",
            [
                ("Can I open this distribution board?", "Можно открыть этот щит?", "you", True, None),
                ("Only if you're competent and authorised.", "Только если компетентен и допущен.", "them", False, None),
                ("I'm waiting for the site electrician.", "Жду электрика объекта.", "you", True, None),
                ("Don't touch live parts meanwhile.", "Пока не трогай токоведущие части.", "them", False, None),
                ("I'll stay clear and watch the area.", "Отойду и прослежу зону.", "you", True, None),
                ("Thanks. Report if anyone removes the cover.", "Спасибо. Скажи, если кто снимет крышку.", "them", False, None),
            ],
            S(("Can I open this distribution board?", "Можно открыть этот щит?"), ("Don't touch live parts.", "Не трогай токоведущие части.")),
        ),
        (
            "Конец induction — вопросы.",
            [
                ("Any questions before you start work?", "Вопросы перед началом работы?", "them", False, None),
                ("Who do I call if I feel unsafe?", "Кому звонить, если небезопасно?", "you", True, None),
                ("Stop work and call me on channel one.", "Стоп работа и звони мне на канал один.", "them", False, None),
                ("Where do I get task briefings?", "Где брать брифинги на задачу?", "you", True, None),
                ("Every morning with your gang.", "Каждое утро со своей бригадой.", "them", False, None),
                ("Understood. I'm ready to start.", "Понял. Готов начинать.", "you", True, None),
            ],
            S(("Who do I call if I feel unsafe?", "Кому звонить, если небезопасно?"), ("I'm ready to start.", "Готов начинать.")),
        ),
    ]
    out = []
    for scene, turns, say in rows:
        out.append((scene, _pair(your, partner, turns), say))
    return out


def build_electrical() -> list:
    your, partner = "electrician", "foreman"
    rows = [
        (
            "Изоляция фидера перед работой.",
            [
                ("Which feeder feeds this board?", "Какой фидер питает этот щит?", "you", True, None),
                ("F3 from the main switchroom.", "F3 из главной электрощитовой.", "them", False, None),
                ("I'll lock it off and prove dead.", "Отключу, повешу замок и проверю отсутствие.", "you", True, None),
                ("Tag it with your name and time.", "Бирка с именем и временем.", "them", False, None),
                ("Done. Safe to open the cover.", "Готово. Можно открывать крышку.", "you", True, None),
                ("Keep one person as a standby.", "Оставь одного наблюдающим.", "them", False, None),
            ],
            S(("Which feeder feeds this board?", "Какой фидер питает щит?"), ("I'll lock it off and prove dead.", "Отключу и проверю отсутствие.")),
        ),
        (
            "Кабель не тот сечением.",
            [
                ("This run is 2.5 but the schedule says 4.", "Тут 2.5, а по спецификации 4.", "you", True, None),
                ("Stop and don't terminate yet.", "Стоп, пока не оконцовывай.", "them", False, None),
                ("Should I pull new cable?", "Тянуть новый кабель?", "you", True, None),
                ("Yes, from the drum in bay two.", "Да, с барабана во втором отсеке.", "them", False, None),
                ("I'll label both ends before I pull.", "Помечу оба конца до протяжки.", "you", True, None),
                ("Good. Update the as‑built after.", "Хорошо. Потом обнови as‑built.", "them", False, None),
            ],
            S(("Schedule says 4.", "По спецификации 4."), ("I'll label both ends.", "Помечу оба конца.")),
        ),
        (
            "Розетка не работает — диагностика.",
            [
                ("Socket in room 12 is dead.", "Розетка в комнате 12 без напряжения.", "you", True, None),
                ("Check the MCB and the RCD first.", "Сначала автомат и УЗО.", "them", False, None),
                ("MCB is on. RCD tripped.", "Автомат включён. УЗО выбило.", "you", True, None),
                ("Find the fault before you reset.", "Найди неисправность до включения.", "them", False, None),
                ("There's a nicked cable in the skirting.", "В плинтусе повреждённый кабель.", "you", True, None),
                ("Repair it, test insulation, then reset.", "Почини, проверь изоляцию, потом включи.", "them", False, None),
            ],
            S(("Socket is dead.", "Розетка без напряжения."), ("RCD tripped.", "УЗО выбило.")),
        ),
        (
            "Подключение светильников.",
            [
                ("Are these fittings LED drivers included?", "В этих светильниках драйверы в комплекте?", "you", True, None),
                ("Yes. Keep polarity correct.", "Да. Соблюдай полярность.", "them", False, None),
                ("Neutral is blue, live brown — OK?", "Ноль синий, фаза коричневый — ок?", "you", True, None),
                ("Yes. Earth to the metal body.", "Да. Землю на металлический корпус.", "them", False, None),
                ("First six are up. Testing next.", "Первые шесть висят. Дальше тест.", "you", True, None),
                ("Megger the circuit before energising.", "Прозвони мегером до подачи.", "them", False, None),
            ],
            S(("Keep polarity correct.", "Соблюдай полярность."), ("Megger before energising.", "Мегер до подачи.")),
        ),
        (
            "Щит — маркировка.",
            [
                ("Half the breakers have no labels.", "У половины автоматов нет подписей.", "you", True, None),
                ("Trace and label before energising the floor.", "Проследи и подпиши до включения этажа.", "them", False, None),
                ("Can I use temporary tags tonight?", "Можно временные бирки на сегодня?", "you", True, None),
                ("Temporary OK, permanent tomorrow.", "Временные ок, постоянные завтра.", "them", False, None),
                ("I'll photo the schedule for the pack.", "Сфоткаю схему для пакета.", "you", True, None),
                ("Add it to the handover folder.", "Положи в папку передачи.", "them", False, None),
            ],
            S(("Breakers have no labels.", "У автоматов нет подписей."), ("Temporary tags tonight.", "Временные бирки на сегодня.")),
        ),
        (
            "Генератор на время отключения.",
            [
                ("Mains outage starts at two.", "Отключение сети в два.", "them", False, None),
                ("Is the generator fuelled?", "Генератор заправлен?", "you", True, None),
                ("Check oil and fuel, then do a test run.", "Проверь масло и топливо, потом тестовый пуск.", "them", False, None),
                ("Test run OK. Changeover ready.", "Тест ок. Готов к переключению.", "you", True, None),
                ("Keep essential circuits only.", "Только важные цепи.", "them", False, None),
                ("Lighting and CCTV only, agreed.", "Только свет и CCTV, договорились.", "you", True, None),
            ],
            S(("Is the generator fuelled?", "Генератор заправлен?"), ("Changeover ready.", "Готов к переключению.")),
        ),
        (
            "Трасса в штробе — глубина.",
            [
                ("How deep should this chase be?", "Какой глубины должна быть штроба?", "you", True, None),
                ("Deep enough for the conduit plus cover.", "Чтобы труба и слой закрытия влезли.", "them", False, None),
                ("Metal or plastic conduit here?", "Металл или пластик здесь?", "you", True, None),
                ("Plastic in walls, metal where exposed.", "Пластик в стенах, металл где открыто.", "them", False, None),
                ("I'll vacuum before plastering.", "Пропылесосю до штукатурки.", "you", True, None),
                ("Don't leave sharp edges on the chase.", "Не оставляй острые края штробы.", "them", False, None),
            ],
            S(("How deep should this chase be?", "Какой глубины штроба?"), ("Plastic in walls.", "Пластик в стенах.")),
        ),
        (
            "Тест УЗО.",
            [
                ("Time to test the RCDs on this board.", "Пора тестить УЗО на этом щите.", "them", False, None),
                ("I'll use the tester and log the times.", "Тестером замерю и запишу времена.", "you", True, None),
                ("Anything over the limit?", "Что-то сверх нормы?", "them", False, None),
                ("One is slow. I'll replace it.", "Одно медленное. Заменю.", "you", True, None),
                ("Retest after replacement.", "После замены перепроверь.", "them", False, None),
                ("Retest passed. Logged.", "Повторный тест ок. Записал.", "you", True, None),
            ],
            S(("I'll log the times.", "Запишу времена."), ("Retest passed.", "Повторный тест ок.")),
        ),
        (
            "Клиент просит доп. розетки.",
            [
                ("Client wants two more sockets in the office.", "Клиент хочет ещё две розетки в офисе.", "you", True, None),
                ("Is there spare capacity on that ring?", "Есть запас по этой кольцевой?", "them", False, None),
                ("Yes, load is low. I can spur carefully.", "Да, нагрузка низкая. Аккуратно сделаю отвод.", "you", True, None),
                ("Get a variation number first.", "Сначала возьми номер вариации.", "them", False, None),
                ("Variation approved. Starting after lunch.", "Вариация одобрена. Начну после обеда.", "you", True, None),
                ("Update drawings when finished.", "Обнови чертежи после.", "them", False, None),
            ],
            S(("Two more sockets in the office.", "Ещё две розетки в офисе."), ("Get a variation number first.", "Сначала номер вариации.")),
        ),
        (
            "Короткое замыкание при включении.",
            [
                ("Breaker trips instantly when I close it.", "Автомат сразу выбивает при включении.", "you", True, None),
                ("Leave it off. Check for a short.", "Оставь выключенным. Ищи КЗ.", "them", False, None),
                ("Found a screw through the cable.", "Нашёл саморез сквозь кабель.", "you", True, None),
                ("Repair the cable and inspect neighbours.", "Почини кабель и проверь соседние.", "them", False, None),
                ("Repair done. Insulation OK.", "Починил. Изоляция ок.", "you", True, None),
                ("Energise with me watching.", "Включай, я смотрю.", "them", False, None),
            ],
            S(("Breaker trips instantly.", "Автомат сразу выбивает."), ("Screw through the cable.", "Саморез сквозь кабель.")),
        ),
        (
            "Уличное освещение.",
            [
                ("Photocell isn't switching the yard lights.", "Фотореле не включает свет во дворе.", "you", True, None),
                ("Bypass it temporarily for tonight?", "На сегодня временно обойти?", "them", False, None),
                ("I can put it on manual until we replace it.", "Поставлю на ручной, пока не заменим.", "you", True, None),
                ("Order a new photocell tomorrow.", "Закажи новое фотореле завтра.", "them", False, None),
                ("Manual is on. Lights stay on overnight.", "Ручной режим. Свет всю ночь.", "you", True, None),
                ("Tell security so they know.", "Скажи охране, чтобы знали.", "them", False, None),
            ],
            S(("Photocell isn't switching.", "Фотореле не включает."), ("Put it on manual.", "Поставь на ручной.")),
        ),
        (
            "Сдача электрики — документы.",
            [
                ("Certificates ready for this floor?", "Сертификаты на этот этаж готовы?", "them", False, None),
                ("IR tests and RCD times are in the folder.", "IR и времена УЗО в папке.", "you", True, True if False else None),
                ("IR tests and RCD times are in the folder.", "IR и времена УЗО в папке.", "you", True, None),
                ("Any open snags?", "Открытые замечания?", "them", False, None),
                ("Two labels left. I'll finish them now.", "Две подписи остались. Сейчас доделаю.", "you", True, None),
                ("Then we can sign off.", "Тогда можем подписывать.", "them", False, None),
            ],
            S(("Certificates ready?", "Сертификаты готовы?"), ("Two labels left.", "Две подписи остались.")),
        ),
    ]
    # fix accidental duplicate line in last script
    rows[-1] = (
        "Сдача электрики — документы.",
        [
            ("Certificates ready for this floor?", "Сертификаты на этот этаж готовы?", "them", False, None),
            ("IR tests and RCD times are in the folder.", "IR и времена УЗО в папке.", "you", True, None),
            ("Any open snags?", "Открытые замечания?", "them", False, None),
            ("Two labels left. I'll finish them now.", "Две подписи остались. Сейчас доделаю.", "you", True, None),
            ("Photo the board schedule too.", "Сфоткай ещё схему щита.", "them", False, None),
            ("Done. Ready to sign off.", "Готово. Можно подписывать.", "you", True, None),
        ],
        S(("Certificates ready?", "Сертификаты готовы?"), ("Ready to sign off.", "Можно подписывать.")),
    )
    return [(scene, _pair(your, partner, turns), say) for scene, turns, say in rows]


def build_tools() -> list:
    your, partner = "electrician", "foreman"
    rows = [
        (
            "Нет нужного бита.",
            [
                ("I need a Torx T20 for these screws.", "Нужен Torx T20 для этих винтов.", "you", True, None),
                ("Check the red case in the van.", "Посмотри красный кейс в фургоне.", "them", False, None),
                ("Found it. Bits were mixed up.", "Нашёл. Биты были перепутаны.", "you", True, None),
                ("Sort the case at break.", "Разложи кейс в перерыв.", "them", False, None),
                ("Will do. Starting these panels now.", "Сделаю. Начинаю эти панели.", "you", True, None),
                ("Don't strip the heads.", "Не сорви шлицы.", "them", False, None),
            ],
            S(("I need a Torx T20.", "Нужен Torx T20."), ("Bits were mixed up.", "Биты были перепутаны.")),
        ),
        (
            "Лазерный уровень сел.",
            [
                ("Laser level battery is dead.", "Батарея лазерного уровня села.", "you", True, None),
                ("Spare is charging in the office.", "Запасная заряжается в офисе.", "them", False, None),
                ("Can I use a spirit level meanwhile?", "Пока обычный уровень можно?", "you", True, None),
                ("Yes for short runs only.", "Да, только на короткие участки.", "them", False, None),
                ("I'll swap batteries in twenty minutes.", "Через двадцать минут поменяю батареи.", "you", True, None),
                ("Bring the empty one back to charge.", "Пустую верни на зарядку.", "them", False, None),
            ],
            S(("Laser level battery is dead.", "Батарея лазера села."), ("Spare is charging.", "Запасная заряжается.")),
        ),
        (
            "Дрель греется.",
            [
                ("The drill is overheating.", "Дрель перегревается.", "you", True, None),
                ("Are you using the right bit for concrete?", "Правильное сверло по бетону?", "them", False, None),
                ("Yes, SDS, but dust is packing the hole.", "Да, SDS, но пыль забивает отверстие.", "you", True, None),
                ("Clear the hole and let the tool cool.", "Прочисти отверстие и дай инструменту остыть.", "them", False, None),
                ("Cooling now. I'll finish after five minutes.", "Стынет. Закончу через пять минут.", "you", True, None),
                ("Use extraction next time.", "В следующий раз с отсосом.", "them", False, None),
            ],
            S(("The drill is overheating.", "Дрель перегревается."), ("Let the tool cool.", "Дай инструменту остыть.")),
        ),
        (
            "Мультиметр чужой — не брать.",
            [
                ("Whose meter is this on the bench?", "Чей мультиметр на верстаке?", "you", True, None),
                ("That's Tom's. Don't take it.", "Тома. Не бери.", "them", False, None),
                ("Mine is in for calibration.", "Мой на калибровке.", "you", True, None),
                ("Borrow the site spare from the store.", "Возьми запасной объекта со склада.", "them", False, None),
                ("Got the spare. Tagged against my name.", "Взял запасной. Записал на себя.", "you", True, None),
                ("Return it before you leave.", "Верни до ухода.", "them", False, None),
            ],
            S(("Whose meter is this?", "Чей мультиметр?"), ("Borrow the site spare.", "Возьми запасной объекта.")),
        ),
        (
            "Стремянка повреждена.",
            [
                ("This step ladder has a bent foot.", "У этой стремянки погнута ножка.", "you", True, None),
                ("Red tag it. Do not use.", "Красную бирку. Не использовать.", "them", False, None),
                ("Where do condemned tools go?", "Куда бракованный инструмент?", "you", True, None),
                ("Quarantine cage by the stores.", "Карантинная клетка у склада.", "them", False, None),
                ("Tagged and moved. Grabbing another.", "Пометил и убрал. Беру другую.", "you", True, None),
                ("Check the next one before you climb.", "Проверь следующую до подъёма.", "them", False, None),
            ],
            S(("Bent foot on the ladder.", "Погнута ножка стремянки."), ("Red tag it.", "Красную бирку.")),
        ),
        (
            "Нужен кабельный нож / стриппер.",
            [
                ("My cable stripper is missing.", "Пропал мой стриппер.", "you", True, None),
                ("Look in the shared toolbox.", "Посмотри в общем ящике.", "them", False, None),
                ("Found it without a handle grip.", "Нашёл без накладки на ручке.", "you", True, None),
                ("Still usable? Or replace?", "Ещё можно? Или менять?", "them", False, None),
                ("I'll replace it — grip is gone.", "Заменю — хват пропал.", "you", True, None),
                ("Put the order on the board.", "Заявку на доску.", "them", False, None),
            ],
            S(("Cable stripper is missing.", "Пропал стриппер."), ("I'll replace it.", "Заменю.")),
        ),
        (
            "Генераторный удлинитель.",
            [
                ("We need a longer lead to the saw.", "Нужен длиннее удлинитель к пиле.", "you", True, None),
                ("Use a 110 volt lead only.", "Только 110‑вольтовый.", "them", False, None),
                ("Is daisy‑chaining allowed?", "Можно соединять несколько?", "you", True, None),
                ("No. One lead, correct length.", "Нет. Один, нужной длины.", "them", False, None),
                ("I'll get the 20 metre yellow lead.", "Возьму жёлтый на 20 метров.", "you", True, None),
                ("Keep it out of puddles.", "Не клади в лужи.", "them", False, None),
            ],
            S(("Longer lead to the saw.", "Длиннее удлинитель к пиле."), ("110 volt lead only.", "Только 110 вольт.")),
        ),
        (
            "Аккумуляторы разряжены.",
            [
                ("Both battery packs are flat.", "Оба аккумулятора сели.", "you", True, None),
                ("Swap with the charged set upstairs.", "Поменяй на заряженные наверху.", "them", False, None),
                ("Charged set is there. Leaving empties on charge.", "Заряженные есть. Пустые ставлю на зарядку.", "you", True, None),
                ("Don't leave packs in the cold van overnight.", "Не оставляй их ночью в холодном фургоне.", "them", False, None),
                ("Understood. I'll bring them inside.", "Понял. Занесу внутрь.", "you", True, None),
                ("Label which pack is weak.", "Пометь, какой слабый.", "them", False, None),
            ],
            S(("Both battery packs are flat.", "Оба аккумулятора сели."), ("Leaving empties on charge.", "Пустые на зарядку.")),
        ),
        (
            "Аренда перфоратора.",
            [
                ("Site SDS drill isn't free. Rent one?", "Объектовый перфоратор занят. Взять в аренду?", "you", True, None),
                ("Call the hire desk for half a day.", "Позвони в прокат на полдня.", "them", False, None),
                ("They can deliver at noon.", "Могут привезти в полдень.", "you", True, None),
                ("Book it. Keep the paperwork.", "Бронируй. Сохрани документы.", "them", False, None),
                ("Booked. Job number is on the docket.", "Забронировал. Номер заказа на накладной.", "you", True, None),
                ("Return with a full battery if cordless.", "Верни с полным зарядом, если аккумуляторный.", "them", False, None),
            ],
            S(("Rent one for half a day?", "Взять в аренду на полдня?"), ("Booked.", "Забронировал.")),
        ),
        (
            "Калибровка динамометрического ключа.",
            [
                ("Torque wrench sticker is out of date.", "Наклейка калибровки на ключе просрочена.", "you", True, None),
                ("Don't use it for terminations then.", "Тогда не используй для оконцовки.", "them", False, None),
                ("Is there a calibrated spare?", "Есть откадиброванный запасной?", "you", True, None),
                ("Yes, blue case in the test kit.", "Да, синий кейс в тест-наборе.", "them", False, None),
                ("Using the blue one. Sending the old for cal.", "Беру синий. Старый отправлю на калибровку.", "you", True, None),
                ("Log the serial in the folder.", "Запиши серийник в папку.", "them", False, None),
            ],
            S(("Torque wrench out of date.", "Ключ просрочен по калибровке."), ("Blue case in the test kit.", "Синий кейс в тест-наборе.")),
        ),
        (
            "Порядок на тележке.",
            [
                ("Tool trolley is a mess again.", "Тележка с инструментом снова в хаосе.", "them", False, None),
                ("I'll sort it before lunch.", "Разложу до обеда.", "you", True, None),
                ("Shadow board stickers are peeling.", "Наклейки теней отклеиваются.", "you", True, None),
                ("Replace them this week.", "Замени на этой неделе.", "them", False, None),
                ("Sorted. Missing one pliers set.", "Разложил. Не хватает одних плоскогубцев.", "you", True, None),
                ("Check the last room you worked in.", "Проверь последнюю комнату, где работал.", "them", False, None),
            ],
            S(("I'll sort the trolley.", "Разложу тележку."), ("Missing one pliers set.", "Не хватает плоскогубцев.")),
        ),
        (
            "Сдача инструмента в конце дня.",
            [
                ("Inventory check in ten minutes.", "Инвентаризация через десять минут.", "them", False, None),
                ("I'll bring everything back to the container.", "Снесу всё в контейнер.", "you", True, None),
                ("Any tool left on site overnight?", "Что-то остаётся на ночь на объекте?", "them", False, None),
                ("No. All back, locked.", "Нет. Всё на месте, закрыто.", "you", True, None),
                ("Sign the sheet then.", "Тогда распишись в листе.", "them", False, None),
                ("Signed. See you tomorrow.", "Подписал. До завтра.", "you", True, None),
            ],
            S(("I'll bring everything back.", "Снесу всё в контейнер."), ("All back, locked.", "Всё на месте, закрыто.")),
        ),
    ]
    return [(scene, _pair(your, partner, turns), say) for scene, turns, say in rows]


ONSITE["induction"] = build_induction()
ONSITE["electrical"] = build_electrical()
ONSITE["tools"] = build_tools()


REGULAR: dict[str, list[tuple[str, list[dict], list[dict]]]] = {}


def build_regular_section(sec_id: str, your: str, partner: str, rows: list) -> None:
    REGULAR[sec_id] = [(scene, _pair(your, partner, turns), say) for scene, turns, say in rows]


build_regular_section(
    "shopping",
    "shopper",
    "assistant",
    [
        (
            "Найти отдел.",
            [
                ("Excuse me, where is the dairy aisle?", "Извините, где молочный отдел?", "you", True, None),
                ("Aisle four, on the left.", "Четвёртый ряд, слева.", "them", False, None),
                ("Do you have oat milk?", "Есть овсяное молоко?", "you", True, None),
                ("Bottom shelf, next to the yoghurt.", "Нижняя полка, рядом с йогуртами.", "them", False, None),
                ("Thanks. I'll grab that.", "Спасибо. Возьму.", "you", True, None),
                ("You're welcome.", "Пожалуйста.", "them", False, None),
            ],
            S(("Where is the dairy aisle?", "Где молочный отдел?"), ("Do you have oat milk?", "Есть овсяное молоко?")),
        ),
        (
            "Нет цены на товаре.",
            [
                ("There's no price on this.", "На этом нет цены.", "you", True, None),
                ("I can scan it for you.", "Могу просканировать.", "them", False, None),
                ("How much is it?", "Сколько стоит?", "you", True, None),
                ("Three euro fifty.", "Три пятьдесят.", "them", False, None),
                ("OK, I'll take it.", "Ок, возьму.", "you", True, None),
                ("Anything else?", "Что-нибудь ещё?", "them", False, None),
            ],
            S(("There's no price on this.", "На этом нет цены."), ("How much is it?", "Сколько стоит?")),
        ),
        (
            "Вернуть товар.",
            [
                ("I'd like to return this jumper.", "Хочу вернуть этот свитер.", "you", True, None),
                ("Have you got the receipt?", "Чек есть?", "them", False, None),
                ("Yes, on my phone.", "Да, в телефоне.", "you", True, None),
                ("Was it washed or worn?", "Стирали или носили?", "them", False, None),
                ("No, tags are still on.", "Нет, бирки на месте.", "you", True, None),
                ("Refund to your card in three days.", "Возврат на карту за три дня.", "them", False, None),
            ],
            S(("I'd like to return this.", "Хочу вернуть это."), ("Tags are still on.", "Бирки на месте.")),
        ),
        (
            "Скидка / акция.",
            [
                ("Is this on offer?", "Это по акции?", "you", True, None),
                ("Buy one get one half price.", "Второй за полцены.", "them", False, None),
                ("Does it work at self‑checkout?", "На кассе самообслуживания сработает?", "you", True, None),
                ("Yes, scan both items.", "Да, пробей оба.", "them", False, None),
                ("Great, I'll take two.", "Отлично, возьму два.", "you", True, None),
                ("The sticker explains it too.", "На стикере тоже написано.", "them", False, None),
            ],
            S(("Is this on offer?", "Это по акции?"), ("I'll take two.", "Возьму два.")),
        ),
        (
            "Нужна помощь с размером.",
            [
                ("Do you have this in a medium?", "Есть такой же medium?", "you", True, None),
                ("I'll check the stockroom.", "Проверю на складе.", "them", False, None),
                ("Any other colours?", "Есть другие цвета?", "you", True, None),
                ("Blue and grey in medium.", "Синий и серый в medium.", "them", False, None),
                ("Blue, please.", "Синий, пожалуйста.", "you", True, None),
                ("Fitting rooms are behind you.", "Примерочные за тобой.", "them", False, None),
            ],
            S(("Do you have this in a medium?", "Есть medium?"), ("Blue, please.", "Синий, пожалуйста.")),
        ),
        (
            "Оплата картой не проходит.",
            [
                ("My card keeps declining.", "Карта всё время отклоняется.", "you", True, None),
                ("Try contactless again, or chip.", "Попробуй ещё contactless или чип.", "them", False, None),
                ("Chip worked. Sorry about that.", "Чип сработал. Извините.", "you", True, None),
                ("No problem. Receipt with you or in the bag?", "Ничего. Чек с собой или в пакет?", "them", False, None),
                ("In the bag, please.", "В пакет, пожалуйста.", "you", True, None),
                ("Have a nice day.", "Хорошего дня.", "them", False, None),
            ],
            S(("My card keeps declining.", "Карта отклоняется."), ("In the bag, please.", "В пакет, пожалуйста.")),
        ),
        (
            "Самообслуживание — помощь.",
            [
                ("The machine says unexpected item.", "Аппарат пишет unexpected item.", "you", True, None),
                ("I'll clear it. Put the bag on the scale.", "Сброшу. Поставь пакет на весы.", "them", False, None),
                ("Do I need to weigh the fruit?", "Фрукты взвешивать?", "you", True, None),
                ("Yes, use the produce code on the screen.", "Да, код овощей/фруктов на экране.", "them", False, None),
                ("Done. It's asking for a bag fee.", "Готово. Просит плату за пакет.", "you", True, None),
                ("Hit yes if you took one.", "Нажми yes, если взял.", "them", False, None),
            ],
            S(("Unexpected item.", "Unexpected item."), ("Do I need to weigh the fruit?", "Фрукты взвешивать?")),
        ),
        (
            "Спросить про аллергены.",
            [
                ("Does this bread contain sesame?", "В этом хлебе есть кунжут?", "you", True, None),
                ("Yes, sesame seeds on top.", "Да, кунжут сверху.", "them", False, None),
                ("Any sesame‑free loaf?", "Есть без кунжута?", "you", True, None),
                ("The plain tin loaf is fine.", "Обычная формовая буханка без него.", "them", False, None),
                ("I'll take that instead.", "Тогда её.", "you", True, None),
                ("Allergy info is on the label too.", "На этикетке тоже есть.", "them", False, None),
            ],
            S(("Does this contain sesame?", "Есть кунжут?"), ("I'll take that instead.", "Тогда её.")),
        ),
        (
            "Заказать торт.",
            [
                ("Can I order a cake for Saturday?", "Можно заказать торт на субботу?", "you", True, None),
                ("What size and flavour?", "Какой размер и вкус?", "them", False, None),
                ("Medium chocolate, name on top: Anna.", "Средний шоколадный, сверху имя Anna.", "you", True, None),
                ("Pickup after two on Saturday.", "Самовывоз после двух в субботу.", "them", False, None),
                ("Can I pay a deposit now?", "Можно депозит сейчас?", "you", True, None),
                ("Twenty euro deposit, rest on pickup.", "Двадцать евро сейчас, остальное при получении.", "them", False, None),
            ],
            S(("Order a cake for Saturday?", "Заказать торт на субботу?"), ("Name on top: Anna.", "Сверху имя Anna.")),
        ),
        (
            "Пакеты / экология.",
            [
                ("I forgot a reusable bag.", "Забыл многоразовую сумку.", "you", True, None),
                ("Paper bags are by the till.", "Бумажные у кассы.", "them", False, None),
                ("How much are they?", "Сколько стоят?", "you", True, None),
                ("Thirty cents each.", "По тридцать центов.", "them", False, None),
                ("Two paper bags, please.", "Две бумажные, пожалуйста.", "you", True, None),
                ("Here you go.", "Держи.", "them", False, None),
            ],
            S(("I forgot a reusable bag.", "Забыл многоразовую сумку."), ("Two paper bags, please.", "Две бумажные.")),
        ),
        (
            "Товар закончился.",
            [
                ("You're out of my usual coffee.", "Моего обычного кофе нет.", "you", True, None),
                ("Next delivery is Thursday.", "Следующая поставка в четверг.", "them", False, None),
                ("Can you recommend a similar one?", "Можете посоветовать похожий?", "you", True, None),
                ("This house brand is close.", "Наша марка похожа.", "them", False, None),
                ("OK, I'll try it.", "Ок, попробую.", "you", True, None),
                ("If you hate it, bring it back unopened.", "Если не зайдёт — верни невскрытым.", "them", False, None),
            ],
            S(("You're out of my usual coffee.", "Моего кофе нет."), ("I'll try it.", "Попробую.")),
        ),
        (
            "Попросить отложить товар.",
            [
                ("Can you hold this jacket until Friday?", "Можете отложить эту куртку до пятницы?", "you", True, None),
                ("I can hold it for forty‑eight hours.", "Могу на сорок восемь часов.", "them", False, None),
                ("That's fine. My name is Kolya.", "Хорошо. Меня зовут Коля.", "you", True, None),
                ("I'll put it behind the desk.", "Положу за стойку.", "them", False, None),
                ("Thanks. I'll come back tomorrow.", "Спасибо. Завтра вернусь.", "you", True, None),
                ("Bring ID when you collect.", "При получении возьми удостоверение.", "them", False, None),
            ],
            S(("Can you hold this until Friday?", "Отложить до пятницы?"), ("I'll come back tomorrow.", "Завтра вернусь.")),
        ),
    ],
)

# Remaining regular sections: travel, home, dating, food, work_office — compact unique scripts
build_regular_section(
    "travel",
    "traveller",
    "agent",
    [
        ("Билет на поезд.", [("I'd like a return to Cork.", "Билет туда‑обратно в Корк.", "you", True, None), ("When are you travelling?", "Когда едете?", "them", False, None), ("Friday morning, back Sunday evening.", "В пятницу утром, обратно в воскресенье вечером.", "you", True, None), ("Off‑peak is cheaper.", "Вне пика дешевле.", "them", False, None), ("Off‑peak is fine.", "Вне пика нормально.", "you", True, None), ("Here's your ticket on the app.", "Билет в приложении.", "them", False, None)], S(("A return to Cork.", "Туда‑обратно в Корк."), ("Off‑peak is fine.", "Вне пика нормально."))),
        ("Задержка рейса.", [("Is the Dublin flight delayed?", "Рейс в Дублин задерживается?", "you", True, None), ("Yes, about forty minutes.", "Да, около сорока минут.", "them", False, None), ("Will I miss my connection?", "Успею на пересадку?", "you", True, None), ("You should still make it.", "Должны успеть.", "them", False, None), ("Where do I get updates?", "Где смотреть обновления?", "you", True, None), ("Boards and the airline app.", "Табло и приложение авиакомпании.", "them", False, None)], S(("Is the flight delayed?", "Рейс задерживается?"), ("Will I miss my connection?", "Успею на пересадку?"))),
        ("Такси / трансфер.", [("How much to the city centre?", "Сколько до центра?", "you", True, None), ("About twenty‑five euro with traffic.", "Около двадцати пяти с пробками.", "them", False, None), ("Can you take card?", "Карту принимаете?", "you", True, None), ("Yes. Seatbelt on, please.", "Да. Пристегнитесь.", "them", False, None), ("Drop me at the hotel entrance.", "Высадите у входа в отель.", "you", True, None), ("Sure.", "Конечно.", "them", False, None)], S(("How much to the city centre?", "Сколько до центра?"), ("Can you take card?", "Карту принимаете?"))),
        ("Отель — ранний заезд.", [("Can I check in early?", "Можно ранний заезд?", "you", True, None), ("Room may be ready after one.", "Номер может быть после часа.", "them", False, None), ("Can I leave my bag?", "Можно оставить сумку?", "you", True, None), ("Yes, luggage room is free.", "Да, камера хранения бесплатна.", "them", False, None), ("Wi‑Fi password?", "Пароль Wi‑Fi?", "you", True, None), ("On your key card sleeve.", "На конверте от ключа.", "them", False, None)], S(("Can I check in early?", "Можно ранний заезд?"), ("Can I leave my bag?", "Можно оставить сумку?"))),
        ("Потерянный багаж.", [("My bag didn't arrive.", "Мой багаж не приехал.", "you", True, None), ("Boarding pass and bag tag, please.", "Посадочный и бирку багажа.", "them", False, None), ("Here's both.", "Вот оба.", "you", True, None), ("We'll deliver it to your hotel.", "Доставим в отель.", "them", False, None), ("How long usually?", "Обычно сколько ждать?", "you", True, None), ("Within twenty‑four hours.", "В течение суток.", "them", False, None)], S(("My bag didn't arrive.", "Багаж не приехал."), ("Deliver it to my hotel.", "Доставьте в отель.")),),
        ("Аренда авто.", [("I have a reservation under Petrov.", "Бронь на Петрова.", "you", True, None), ("Licence and credit card, please.", "Права и кредитку.", "them", False, None), ("Full insurance included?", "Полная страховка включена?", "you", True, None), ("Basic is included; excess is five hundred.", "Базовая да; франшиза пятьсот.", "them", False, None), ("I'll take the extra cover.", "Возьму доп. покрытие.", "you", True, None), ("Car is in bay twelve.", "Машина на месте двенадцать.", "them", False, None)], S(("Reservation under Petrov.", "Бронь на Петрова."), ("I'll take the extra cover.", "Возьму доп. покрытие.")),),
        ("Спросить дорогу.", [("How do I get to the museum?", "Как пройти к музею?", "you", True, None), ("Straight, then left at the lights.", "Прямо, потом налево на светофоре.", "them", False, None), ("Is it walkable?", "Пешком нормально?", "you", True, None), ("Ten minutes.", "Минут десять.", "them", False, None), ("Thanks a lot.", "Большое спасибо.", "you", True, None), ("Enjoy your visit.", "Приятного визита.", "them", False, None)], S(("How do I get to the museum?", "Как пройти к музею?"), ("Is it walkable?", "Пешком нормально?") ),),
        ("Обмен валюты.", [("Can I change euros to pounds?", "Можно евро на фунты?", "you", True, None), ("Passport needed over five hundred.", "Паспорт если больше пятисот.", "them", False, None), ("Two hundred only.", "Только двести.", "you", True, None), ("Rate is on the board.", "Курс на табло.", "them", False, None), ("OK, go ahead.", "Ок, меняйте.", "you", True, None), ("Count it before you leave.", "Пересчитайте до ухода.", "them", False, None)], S(("Change euros to pounds?", "Евро на фунты?"), ("Two hundred only.", "Только двести.")),),
        ("Билет в музей.", [("Two adults, please.", "Два взрослых.", "you", True, None), ("Any student discount?", "Студенческая скидка?", "them", False, None), ("Yes, here's my card.", "Да, вот карта.", "you", True, None), ("Audio guide included?", "Аудиогид включён?", "them", False, None), ("Extra three euro.", "Плюс три евро.", "you", True, None), ("Yes, two audio guides.", "Да, два аудиогида.", "you", True, None)], S(("Two adults, please.", "Два взрослых."), ("Audio guide included?", "Аудиогид включён?") ),),
        ("Пропущенная остановка.", [("I missed my stop.", "Я проехал свою остановку.", "you", True, None), ("Next one is fine; walk back five minutes.", "Следующая ок; назад пять минут пешком.", "them", False, None), ("Do I need a new ticket?", "Нужен новый билет?", "you", True, None), ("No, stay on.", "Нет, оставайтесь.", "them", False, None), ("Thanks for the help.", "Спасибо за помощь.", "you", True, None), ("Press stop when you see the park.", "Нажмите stop у парка.", "them", False, None)], S(("I missed my stop.", "Проехал остановку."), ("Do I need a new ticket?", "Нужен новый билет?") ),),
        ("Регистрация на рейс онлайн не работает.", [("Online check‑in failed.", "Онлайн‑регистрация не прошла.", "you", True, None), ("Use the desk; passport ready.", "Идите на стойку; паспорт готовьте.", "them", False, None), ("Any extra fee?", "Доплата будет?", "you", True, None), ("No fee at the desk today.", "Сегодня на стойке без доплаты.", "them", False, None), ("Window seat if possible.", "У окна, если можно.", "you", True, None), ("Done. Gate B12.", "Готово. Выход B12.", "them", False, None)], S(("Online check‑in failed.", "Онлайн‑регистрация не прошла."), ("Window seat if possible.", "У окна, если можно.") ),),
        ("Отмена брони отеля.", [("I need to cancel my booking.", "Нужно отменить бронь.", "you", True, None), ("What's the booking reference?", "Номер брони?", "them", False, None), ("H78421.", "H78421.", "you", True, None), ("Free cancellation until six tonight.", "Бесплатная отмена до шести вечера.", "them", False, None), ("Please cancel it.", "Отмените, пожалуйста.", "you", True, None), ("Cancelled. Email confirmation sent.", "Отменено. Письмо отправили.", "them", False, None)], S(("I need to cancel my booking.", "Нужно отменить бронь."), ("Please cancel it.", "Отмените.") ),),
    ],
)

build_regular_section(
    "home",
    "tenant",
    "landlord",
    [
        ("Протечка крана.", [("The kitchen tap is leaking.", "Кухонный кран течёт.", "you", True, None), ("Drops or a steady stream?", "Капает или струя?", "them", False, None), ("Steady under the handle.", "Струя из‑под ручки.", "you", True, None), ("I'll send a plumber tomorrow.", "Пришлю сантехника завтра.", "them", False, None), ("Can I shut the valve myself?", "Могу сам перекрыть вентиль?", "you", True, None), ("Yes, under the sink.", "Да, под раковиной.", "them", False, None)], S(("The kitchen tap is leaking.", "Кран течёт."), ("I'll send a plumber tomorrow.", "Пришлю сантехника завтра.")),),
        ("Отопление не работает.", [("Heating won't turn on.", "Отопление не включается.", "you", True, None), ("Is the boiler showing an error?", "На котле ошибка?", "them", False, None), ("Yes, code E3.", "Да, код E3.", "you", True, None), ("Reset once; if it returns, call me.", "Сбрось раз; если вернётся — звони.", "them", False, None), ("Reset done. Still E3.", "Сбросил. Всё ещё E3.", "you", True, None), ("Engineer today after four.", "Мастер сегодня после четырёх.", "them", False, None)], S(("Heating won't turn on.", "Отопление не включается."), ("Code E3.", "Код E3.")),),
        ("Соседи шумят.", [("Neighbours are loud after eleven.", "Соседи шумят после одиннадцати.", "you", True, None), ("Have you spoken to them?", "Говорил с ними?", "them", False, None), ("Not yet. Wanted to ask you first.", "Ещё нет. Сначала хотел спросить вас.", "you", True, None), ("Try a polite note; then I'll step in.", "Сначала вежливая записка; потом подключусь.", "them", False, None), ("OK, I'll note tonight.", "Ок, сегодня оставлю записку.", "you", True, None), ("Keep a simple log of times.", "Веди простой лог по времени.", "them", False, None)], S(("Neighbours are loud after eleven.", "Соседи шумят после одиннадцати."), ("I'll note tonight.", "Сегодня оставлю записку.")),),
        ("Аренда — продление.", [("Can we renew for another year?", "Можем продлить ещё на год?", "you", True, None), ("Rent may rise by five percent.", "Аренда может вырасти на пять процентов.", "them", False, None), ("Is that negotiable?", "Можно обсудить?", "you", True, None), ("I can do three percent if you sign early.", "Могу три процента, если подпишете рано.", "them", False, None), ("We'll sign next week.", "Подпишем на следующей неделе.", "you", True, None), ("I'll email the new agreement.", "Пришлю новый договор.", "them", False, None)], S(("Can we renew?", "Можем продлить?"), ("We'll sign next week.", "Подпишем на следующей неделе.")),),
        ("Ключи / доступ.", [("I lost my spare key.", "Потерял запасной ключ.", "you", True, None), ("I can cut a new one for twenty euro.", "Могу сделать новый за двадцать евро.", "them", False, None), ("Please do. When?", "Сделайте. Когда?", "you", True, None), ("Friday morning.", "В пятницу утром.", "them", False, None), ("Should I change the lock?", "Менять замок?", "you", True, None), ("Not unless you're worried.", "Только если переживаете.", "them", False, None)], S(("I lost my spare key.", "Потерял запасной ключ."), ("Friday morning.", "В пятницу утром.")),),
        ("Интернет дома.", [("Wi‑Fi keeps dropping.", "Wi‑Fi постоянно отваливается.", "you", True, None), ("Is the router lights normal?", "Индикаторы роутера в норме?", "them", False, None), ("WAN light is red.", "WAN красный.", "you", True, None), ("Reboot the modem; wait two minutes.", "Перезагрузи модем; подожди две минуты.", "them", False, None), ("Still red after reboot.", "После ребута всё ещё красный.", "you", True, None), ("I'll raise a ticket with the ISP.", "Открою заявку у провайдера.", "them", False, None)], S(("Wi‑Fi keeps dropping.", "Wi‑Fi отваливается."), ("WAN light is red.", "WAN красный.")),),
        ("Стиралка течёт.", [("Washing machine leaked on the floor.", "Стиралка залила пол.", "you", True, None), ("Turn off water and power.", "Перекрой воду и питание.", "them", False, None), ("Done. Towels down.", "Сделано. Полотенца на полу.", "you", True, None), ("Don't run it again.", "Больше не включай.", "them", False, None), ("Can you arrange a repair?", "Организуете ремонт?", "you", True, None), ("Yes, tomorrow afternoon.", "Да, завтра после обеда.", "them", False, None)], S(("Washing machine leaked.", "Стиралка течёт."), ("Turn off water and power.", "Перекрой воду и питание.")),),
        ("Гости / правила дома.", [("Can two friends stay for the weekend?", "Могут двое друзей остаться на выходные?", "you", True, None), ("Yes, under a week is fine.", "Да, меньше недели ок.", "them", False, None), ("Any quiet hours?", "Есть тихие часы?", "you", True, None), ("After ten, keep it down.", "После десяти — потише.", "them", False, None), ("Understood. Thanks.", "Понял. Спасибо.", "you", True, None), ("Message me their names for the gate.", "Напиши имена для шлагбаума.", "them", False, None)], S(("Friends stay for the weekend?", "Друзья на выходные?"), ("After ten, keep it down.", "После десяти потише.")),),
        ("Счёт за электричество.", [("The electricity bill looks high.", "Счёт за свет кажется большим.", "you", True, None), ("Compare to last winter.", "Сравни с прошлой зимой.", "them", False, None), ("It's thirty percent higher.", "На тридцать процентов выше.", "you", True, None), ("Check for heaters left on.", "Проверь, не оставлены ли обогреватели.", "them", False, None), ("I'll check tonight.", "Проверю сегодня вечером.", "you", True, None), ("Send me a photo of the meter.", "Пришли фото счётчика.", "them", False, None)], S(("Bill looks high.", "Счёт большой."), ("Thirty percent higher.", "На тридцать процентов выше.")),),
        ("Парковка у дома.", [("Someone blocked my space.", "Кто-то занял моё место.", "you", True, None), ("Is it a visitor space?", "Гостевое?", "them", False, None), ("No, mine — number 14.", "Нет, моё — 14.", "you", True, None), ("I'll message the group chat.", "Напишу в общий чат.", "them", False, None), ("Thanks. I need to leave for work.", "Спасибо. Мне на работу.", "you", True, None), ("Use the visitor bay meantime.", "Пока встань на гостевое.", "them", False, None)], S(("Someone blocked my space.", "Заняли моё место."), ("Number 14.", "Номер 14.")),),
        ("Заселение — опись.", [("Can we do the inventory together?", "Можем вместе пройти опись?", "you", True, None), ("Yes, this afternoon.", "Да, сегодня после обеда.", "them", False, None), ("There's a scratch on the fridge.", "На холодильнике царапина.", "you", True, None), ("Photo and note it.", "Фото и в заметки.", "them", False, None), ("Done. Anything else to check?", "Готово. Что ещё проверить?", "you", True, None), ("Meters and keys next.", "Дальше счётчики и ключи.", "them", False, None)], S(("Inventory together?", "Опись вместе?"), ("Scratch on the fridge.", "Царапина на холодильнике.")),),
        ("Выселение — уборка.", [("What cleaning is required to leave?", "Какая уборка нужна при выезде?", "you", True, None), ("Oven, fridge, floors, bathrooms.", "Духовка, холодильник, полы, ванные.", "them", False, None), ("Professional clean mandatory?", "Профчистка обязательна?", "you", True, None), ("Not if you leave it spotless.", "Нет, если оставите идеально.", "them", False, None), ("I'll book a cleaner anyway.", "Всё равно вызову клинера.", "you", True, None), ("Keep receipts for the deposit.", "Чеки сохрани для депозита.", "them", False, None)], S(("What cleaning is required?", "Какая уборка нужна?"), ("I'll book a cleaner.", "Вызову клинера.")),),
    ],
)

build_regular_section(
    "dating",
    "you",
    "them",
    [
        ("Предложить встречу.", [("Would you like to grab coffee this week?", "Не хочешь кофе на этой неделе?", "you", True, None), ("Sure. I'm free Thursday evening.", "Да. В четверг вечером свободен/свободна.", "them", False, None), ("Great. Five at the cafe on Main Street?", "Отлично. В пять в кафе на Main Street?", "you", True, None), ("Perfect. See you then.", "Идеально. Тогда увидимся.", "them", False, None), ("I'll text you when I'm nearby.", "Напишу, когда буду рядом.", "you", True, None), ("Sounds good.", "Договорились.", "them", False, None)], S(("Grab coffee this week?", "Кофе на этой неделе?"), ("Five at the cafe.", "В пять в кафе.")),),
        ("Перенести встречу.", [("Can we move Friday to Saturday?", "Можно перенести пятницу на субботу?", "you", True, None), ("What happened?", "Что случилось?", "them", False, None), ("Work ran late. Sorry.", "Работа затянулась. Извини.", "you", True, None), ("Saturday afternoon works.", "Суббота после обеда ок.", "them", False, None), ("Thanks for being flexible.", "Спасибо, что гибко.", "you", True, None), ("No stress.", "Без стресса.", "them", False, None)], S(("Move Friday to Saturday?", "Перенести на субботу?"), ("Thanks for being flexible.", "Спасибо, что гибко.")),),
        ("Выбрать место.", [("Movie or a walk in the park?", "Кино или прогулка в парке?", "you", True, None), ("Park if the weather holds.", "Парк, если погода держится.", "them", False, None), ("There's a nice path by the river.", "Есть хороший путь у реки.", "you", True, None), ("Let's do that.", "Давай так.", "them", False, None), ("I can bring coffee.", "Могу взять кофе.", "you", True, None), ("I'll bring snacks.", "Я принесу перекус.", "them", False, None)], S(("Movie or a walk?", "Кино или прогулка?"), ("Path by the river.", "Путь у реки.")),),
        ("Первый разговор — хобби.", [("What do you usually do on weekends?", "Чем обычно занимаешься на выходных?", "you", True, None), ("I run and cook a bit.", "Бегаю и немного готовлю.", "them", False, None), ("I like photography.", "Люблю фотографию.", "you", True, None), ("Maybe we shoot by the harbour sometime.", "Может, снимем у гавани как‑нибудь.", "them", False, None), ("I'd like that.", "Мне бы понравилось.", "you", True, None), ("Deal.", "Договорились.", "them", False, None)], S(("What do you do on weekends?", "Чем на выходных?"), ("I like photography.", "Люблю фотографию.")),),
        ("Оплатить счёт.", [("Shall we split the bill?", "Разделим счёт?", "you", True, None), ("I can get this one.", "Этот могу я.", "them", False, None), ("Next one's on me then.", "Тогда следующий за мной.", "you", True, None), ("Fair.", "Справедливо.", "them", False, None), ("Card or cash?", "Карта или наличные?", "you", True, None), ("Card is fine.", "Карта ок.", "them", False, None)], S(("Shall we split the bill?", "Разделим счёт?"), ("Next one's on me.", "Следующий за мной.")),),
        ("Знакомство с друзьями.", [("A few friends are at a gig tonight. Want to join?", "Друзья идут на концерт. Хочешь с нами?", "you", True, None), ("What kind of music?", "Какая музыка?", "them", False, None), ("Indie, not too loud.", "Инди, не слишком громко.", "you", True, None), ("OK, I'll come for an hour.", "Ок, зайду на час.", "them", False, None), ("I'll introduce you to Sam.", "Познакомлю с Сэмом.", "you", True, None), ("Looking forward to it.", "Жду с интересом.", "them", False, None)], S(("Want to join a gig?", "Хочешь на концерт?"), ("I'll come for an hour.", "Зайду на час.")),),
        ("Границы — медленнее.", [("I like hanging out. Can we take it slow?", "Мне нравится общаться. Можем помедленнее?", "you", True, None), ("Of course. Thanks for saying it.", "Конечно. Спасибо, что сказал(а).", "them", False, None), ("Texting is fine; no pressure for late nights.", "Переписка ок; без давления на поздние встречи.", "you", True, None), ("Agreed.", "Согласен/согласна.", "them", False, None), ("Coffee Sunday still good?", "Кофе в воскресенье ещё в силе?", "you", True, None), ("Yes. Looking forward.", "Да. Жду.", "them", False, None)], S(("Can we take it slow?", "Можем помедленнее?"), ("Coffee Sunday still good?", "Кофе в воскресенье ок?") ),),
        ("Онлайн‑чат — предложить звонок.", [("Want to hop on a quick call?", "Хочешь быстро созвониться?", "you", True, None), ("Give me ten minutes.", "Дай десять минут.", "them", False, None), ("WhatsApp or FaceTime?", "WhatsApp или FaceTime?", "you", True, None), ("WhatsApp.", "WhatsApp.", "them", False, None), ("Calling now.", "Звоню.", "you", True, None), ("Hey!", "Привет!", "them", False, None)], S(("Hop on a quick call?", "Быстро созвониться?"), ("WhatsApp or FaceTime?", "WhatsApp или FaceTime?") ),),
        ("Комплимент без давления.", [("That jacket looks great on you.", "Куртка тебе очень идёт.", "you", True, None), ("Thanks, I just got it.", "Спасибо, только купил(а).", "them", False, None), ("Where from?", "Где?", "you", True, None), ("The shop near the bridge.", "Магазин у моста.", "them", False, None), ("Good find.", "Удачная находка.", "you", True, None), ("Appreciate it.", "Приятно.", "them", False, None)], S(("That jacket looks great.", "Куртка очень идёт."), ("Good find.", "Удачная находка.") ),),
        ("После встречи — follow‑up.", [("I had a really nice time today.", "Мне сегодня было очень приятно.", "you", True, None), ("Same here.", "Мне тоже.", "them", False, None), ("Want to do it again next week?", "Повторим на следующей неделе?", "you", True, None), ("Yes. Midweek?", "Да. Середина недели?", "them", False, None), ("Wednesday works.", "Среда подходит.", "you", True, None), ("It's a plan.", "Договорились.", "them", False, None)], S(("I had a nice time.", "Было приятно."), ("Wednesday works.", "Среда подходит.") ),),
        ("Отказ вежливо.", [("I don't think we're a match, but I enjoyed chatting.", "Думаю, мы не пара, но общаться было приятно.", "you", True, None), ("Thanks for being honest.", "Спасибо за честность.", "them", False, None), ("No hard feelings.", "Без обид.", "you", True, None), ("None. Take care.", "Конечно. Береги себя.", "them", False, None), ("You too.", "И ты.", "you", True, None), ("Bye.", "Пока.", "them", False, None)], S(("I don't think we're a match.", "Мы не пара."), ("No hard feelings.", "Без обид.") ),),
        ("Безопасность первой встречи.", [("Let's meet in a public cafe first.", "Давай сначала в публичном кафе.", "you", True, None), ("Agreed. Daytime?", "Согласен. Днём?", "them", False, None), ("Saturday at two.", "В субботу в два.", "you", True, None), ("I'll tell a friend where I am.", "Скажу другу, где я.", "them", False, None), ("Same. See you Saturday.", "Я тоже. До субботы.", "you", True, None), ("See you.", "До встречи.", "them", False, None)], S(("Public cafe first.", "Сначала публичное кафе."), ("Saturday at two.", "В субботу в два.") ),),
    ],
)

build_regular_section(
    "food",
    "guest",
    "waiter",
    [
        ("Стол на двоих.", [("Table for two, please.", "Столик на двоих.", "you", True, None), ("Inside or outside?", "Внутри или на улице?", "them", False, None), ("Inside, near the window if possible.", "Внутри, у окна если можно.", "you", True, None), ("Right this way.", "Сюда, пожалуйста.", "them", False, None), ("Could we see the menu?", "Можно меню?", "you", True, None), ("Here you are.", "Держите.", "them", False, None)], S(("Table for two.", "Столик на двоих."), ("Near the window.", "У окна.")),),
        ("Аллергия.", [("I have a nut allergy.", "У меня аллергия на орехи.", "you", True, None), ("I'll mark it on the order.", "Отмечу в заказе.", "them", False, None), ("Is the sauce safe?", "Соус безопасный?", "you", True, None), ("I'll check with the kitchen.", "Уточню на кухне.", "them", False, None), ("Thanks. I'll wait.", "Спасибо. Подожду.", "you", True, None), ("Chef confirms it's nut‑free.", "Шеф подтвердил — без орехов.", "them", False, None)], S(("I have a nut allergy.", "Аллергия на орехи."), ("Is the sauce safe?", "Соус безопасный?") ),),
        ("Рекомендация блюда.", [("What do you recommend?", "Что посоветуете?", "you", True, None), ("The fish of the day is popular.", "Рыба дня популярна.", "them", False, None), ("Is it spicy?", "Острая?", "you", True, None), ("Mild. We can add chilli.", "Мягкая. Можно добавить чили.", "them", False, None), ("Mild is fine. I'll take it.", "Мягкая ок. Возьму.", "you", True, None), ("Side salad or chips?", "Салат или картошка?", "them", False, None)], S(("What do you recommend?", "Что посоветуете?"), ("Mild is fine.", "Мягкая ок.") ),),
        ("Изменить заказ.", [("Can I change the fries to salad?", "Можно вместо картошки салат?", "you", True, None), ("No problem.", "Без проблем.", "them", False, None), ("And no onions, please.", "И без лука, пожалуйста.", "you", True, None), ("Noted.", "Записал.", "them", False, None), ("How long for the mains?", "Сколько ждать основное?", "you", True, None), ("About fifteen minutes.", "Минут пятнадцать.", "them", False, None)], S(("Fries to salad?", "Вместо картошки салат?"), ("No onions, please.", "Без лука.") ),),
        ("Счёт и чаевые.", [("Could we get the bill?", "Можно счёт?", "you", True, None), ("Together or separate?", "Вместе или раздельно?", "them", False, None), ("Together, please.", "Вместе.", "you", True, None), ("Card machine is coming.", "Терминал сейчас.", "them", False, None), ("Is service included?", "Сервис включён?", "you", True, None), ("No, tipping is optional.", "Нет, чаевые по желанию.", "them", False, None)], S(("Could we get the bill?", "Можно счёт?"), ("Is service included?", "Сервис включён?") ),),
        ("Бронь не нашли.", [("I booked under Ivanov at seven.", "Бронь на Иванова на семь.", "you", True, None), ("I don't see it. Any phone number?", "Не вижу. Номер телефона?", "them", False, None), ("087…", "087…", "you", True, None), ("Found it under a different spelling.", "Нашли под другим написанием.", "them", False, None), ("Table ready now?", "Столик сейчас готов?", "you", True, None), ("Five minutes at the bar.", "Пять минут у бара.", "them", False, None)], S(("Booked under Ivanov.", "Бронь на Иванова."), ("Found it.", "Нашли.") ),),
        ("Брать с собой.", [("Can I get this to go?", "Можно с собой?", "you", True, None), ("Sure. Cutlery?", "Конечно. Приборы?", "them", False, None), ("Yes, please.", "Да, пожалуйста.", "you", True, None), ("It'll be two minutes.", "Минуты две.", "them", False, None), ("Extra napkins if possible.", "Ещё салфетки, если можно.", "you", True, None), ("Here you go.", "Держите.", "them", False, None)], S(("Can I get this to go?", "Можно с собой?"), ("Extra napkins.", "Ещё салфетки.") ),),
        ("Кофейня — заказ.", [("Flat white and a croissant, please.", "Флэт уайт и круассан.", "you", True, None), ("For here or takeaway?", "Здесь или с собой?", "them", False, None), ("For here.", "Здесь.", "you", True, None), ("Any syrup?", "Сироп?", "them", False, None), ("No, thanks.", "Нет, спасибо.", "you", True, None), ("Name for the cup?", "Имя на стакан?", "them", False, None)], S(("Flat white and a croissant.", "Флэт уайт и круассан."), ("For here.", "Здесь.") ),),
        ("Блюдо не то.", [("Sorry, this isn't what I ordered.", "Извините, это не мой заказ.", "you", True, None), ("What did you order?", "Что вы заказывали?", "them", False, None), ("The pasta without chicken.", "Пасту без курицы.", "you", True, None), ("I'll replace it right away.", "Сейчас заменю.", "them", False, None), ("Thank you.", "Спасибо.", "you", True, None), ("Sorry for the mix‑up.", "Извините за путаницу.", "them", False, None)], S(("This isn't what I ordered.", "Это не мой заказ."), ("Pasta without chicken.", "Паста без курицы.") ),),
        ("Веган‑опции.", [("Do you have vegan mains?", "Есть веганские основные?", "you", True, None), ("The chickpea stew and the salad bowl.", "Рагу из нута и салат‑боул.", "them", False, None), ("Is the bread vegan?", "Хлеб веганский?", "you", True, None), ("Yes, the sourdough is.", "Да, заквасочный.", "them", False, None), ("Chickpea stew, please.", "Рагу из нута, пожалуйста.", "you", True, None), ("Great choice.", "Хороший выбор.", "them", False, None)], S(("Vegan mains?", "Веганские основные?"), ("Chickpea stew, please.", "Рагу из нута.") ),),
        ("Слишком долго ждать.", [("We've been waiting thirty minutes.", "Ждём уже тридцать минут.", "you", True, None), ("I'll check the kitchen now.", "Сейчас уточню на кухне.", "them", False, None), ("Any idea how much longer?", "Сколько ещё примерно?", "you", True, None), ("Five minutes, or I can comp a drink.", "Минут пять, или комплимент‑напиток.", "them", False, None), ("A drink would help, thanks.", "Напиток поможет, спасибо.", "you", True, None), ("On the way.", "Уже несут.", "them", False, None)], S(("Waiting thirty minutes.", "Ждём тридцать минут."), ("A drink would help.", "Напиток поможет.") ),),
        ("Десерт / кофе после.", [("Could we see the dessert menu?", "Можно меню десертов?", "you", True, None), ("Chocolate cake or apple crumble.", "Шоколадный торт или яблочный крамбл.", "them", False, None), ("Crumble with ice cream.", "Крамбл с мороженым.", "you", True, None), ("Coffee as well?", "Кофе тоже?", "them", False, None), ("Two americano.", "Два американо.", "you", True, None), ("Coming up.", "Сейчас будет.", "them", False, None)], S(("Dessert menu?", "Меню десертов?"), ("Crumble with ice cream.", "Крамбл с мороженым.") ),),
    ],
)

build_regular_section(
    "work_office",
    "employee",
    "manager",
    [
        ("Статус задачи.", [("Quick update on the report?", "Коротко по статусу отчёта?", "them", False, None), ("Draft is ready; need your numbers.", "Черновик готов; нужны ваши цифры.", "you", True, None), ("I'll send them by noon.", "Пришлю до полудня.", "them", False, None), ("Then I can finish today.", "Тогда закончу сегодня.", "you", True, None), ("Put it on the shared drive.", "Положи на общий диск.", "them", False, None), ("Will do.", "Сделаю.", "you", True, None)], S(("Draft is ready.", "Черновик готов."), ("Finish today.", "Закончу сегодня.")),),
        ("Просить дедлайн.", [("Can we push the deadline to Friday?", "Можно сдвинуть дедлайн на пятницу?", "you", True, None), ("What's blocking you?", "Что блокирует?", "them", False, None), ("Waiting on legal review.", "Ждём ревью юристов.", "you", True, None), ("Friday is OK if you flag risks.", "Пятница ок, если отметишь риски.", "them", False, None), ("I'll add a risk note today.", "Добавлю заметку о рисках сегодня.", "you", True, None), ("Thanks.", "Спасибо.", "them", False, None)], S(("Push the deadline to Friday?", "Сдвинуть на пятницу?"), ("Waiting on legal.", "Ждём юристов.")),),
        ("Созвон / календарь.", [("Can we move the call to three?", "Можно перенести созвон на три?", "you", True, None), ("I have a conflict at three.", "В три конфликт.", "them", False, None), ("Four thirty instead?", "Тогда в четыре тридцать?", "you", True, None), ("Works. Send an invite.", "Подходит. Пришли инвайт.", "them", False, None), ("Invite sent with the agenda.", "Инвайт с повесткой ушёл.", "you", True, None), ("Perfect.", "Отлично.", "them", False, None)], S(("Move the call to three?", "Перенести на три?"), ("Four thirty instead?", "В четыре тридцать?") ),),
        ("Больничный.", [("I need to take a sick day.", "Нужен больничный день.", "you", True, None), ("Feel better. Update the team chat.", "Выздоравливай. Напиши в чат команды.", "them", False, None), ("Can someone cover the standup?", "Кто‑то может закрыть стендап?", "you", True, None), ("I'll cover it.", "Я закрою.", "them", False, None), ("Thanks. Back tomorrow if I'm better.", "Спасибо. Завтра выйду, если лучше.", "you", True, None), ("No rush.", "Не торопись.", "them", False, None)], S(("I need a sick day.", "Нужен больничный."), ("Someone cover standup?", "Кто закроет стендап?") ),),
        ("Обратная связь.", [("Can I get feedback on my draft?", "Можно фидбек по черновику?", "you", True, None), ("Overall clear. Shorten the intro.", "В целом ясно. Сократи введение.", "them", False, None), ("Any issues with the data?", "Проблемы с данными?", "you", True, None), ("Source the second chart.", "Укажи источник второго графика.", "them", False, None), ("I'll revise this afternoon.", "Переделаю после обеда.", "you", True, None), ("Ping me when it's up.", "Напиши, когда будет.", "them", False, None)], S(("Feedback on my draft?", "Фидбек по черновику?"), ("Shorten the intro.", "Сократи введение.") ),),
        ("Новый коллега.", [("This is Ana, joining our team.", "Это Ана, к нам в команду.", "them", False, None), ("Welcome. I handle onboarding docs.", "Добро пожаловать. Я по документам онбординга.", "you", True, None), ("She'll need access to the CRM.", "Ей нужен доступ к CRM.", "them", False, None), ("I'll request it today.", "Запрошу сегодня.", "you", True, None), ("Give her a tour after lunch.", "Проведи экскурсию после обеда.", "them", False, None), ("Happy to.", "С удовольствием.", "you", True, None)], S(("Welcome to the team.", "Добро пожаловать."), ("I'll request CRM access.", "Запрошу доступ к CRM.") ),),
        ("Принтер / офисная техника.", [("The printer on floor two is jammed.", "Принтер на втором зажевал бумагу.", "you", True, None), ("Did you open the side panel?", "Открывал боковую панель?", "them", False, None), ("Yes, still stuck.", "Да, всё ещё застряло.", "you", True, None), ("Call facilities on extension 200.", "Позвони facilities на 200.", "them", False, None), ("I'll call now.", "Звоню сейчас.", "you", True, None), ("Use floor one meantime.", "Пока печатай на первом.", "them", False, None)], S(("Printer is jammed.", "Принтер зажевал."), ("Call facilities.", "Позвони facilities.") ),),
        ("Удалёнка.", [("Can I work from home Thursday?", "Можно в четверг из дома?", "you", True, None), ("Any meetings on site?", "Есть встречи в офисе?", "them", False, None), ("Only online standups.", "Только онлайн‑стендапы.", "you", True, None), ("OK. Be online by nine.", "Ок. Будь онлайн к девяти.", "them", False, None), ("Will be. Thanks.", "Буду. Спасибо.", "you", True, None), ("Update the calendar status.", "Обнови статус в календаре.", "them", False, None)], S(("Work from home Thursday?", "В четверг из дома?"), ("Be online by nine.", "Онлайн к девяти.") ),),
        ("Конфликт приоритетов.", [("Two deadlines clash tomorrow.", "Завтра два дедлайна пересекаются.", "you", True, None), ("Which is client‑facing?", "Что для клиента?", "them", False, None), ("The proposal is client‑facing.", "Предложение — для клиента.", "you", True, None), ("Do that first; slip the internal doc.", "Сначала его; внутренний можно сдвинуть.", "them", False, None), ("I'll tell the other owner.", "Скажу другому владельцу.", "you", True, None), ("Copy me on that message.", "Скопируй меня в том сообщении.", "them", False, None)], S(("Two deadlines clash.", "Два дедлайна пересекаются."), ("Client‑facing first.", "Сначала клиентское.") ),),
        ("Подготовка к презентации.", [("Slides ready for the demo?", "Слайды к демо готовы?", "them", False, None), ("Almost. Need the latest metrics.", "Почти. Нужны свежие метрики.", "you", True, None), ("I'll paste them in shared notes.", "Вставлю в общие заметки.", "them", False, None), ("I'll lock slides by five.", "Закрою слайды к пяти.", "you", True, None), ("Rehearse once with me.", "Один раз прогоним вместе.", "them", False, None), ("After lunch works.", "После обеда подходит.", "you", True, None)], S(("Need the latest metrics.", "Нужны свежие метрики."), ("Lock slides by five.", "Закрою слайды к пяти.") ),),
        ("Зарплата / payroll вопрос.", [("My payslip looks short this month.", "Зарплатный лист в этом месяце меньше.", "you", True, None), ("Overtime missing?", "Овертайм не учли?", "them", False, None), ("Yes, last week's hours.", "Да, часы прошлой недели.", "you", True, None), ("Send timesheet to payroll today.", "Отправь табель в payroll сегодня.", "them", False, None), ("Sent. Can it correct this run?", "Отправил. Успеют в этом расчёте?", "you", True, None), ("If not, next cycle with backpay.", "Если нет — в следующем с доплатой.", "them", False, None)], S(("Payslip looks short.", "Зарплата меньше."), ("Overtime missing.", "Овертайм не учли.") ),),
        ("Конец дня — хэндовер.", [("Before I leave: open items?", "Перед уходом: открытые задачи?", "you", True, None), ("Follow up with the vendor tomorrow.", "Завтра дожми вендора.", "them", False, None), ("I'll set a reminder at nine.", "Поставлю напоминание на девять.", "you", True, None), ("Anything urgent tonight?", "Что‑то срочное на вечер?", "them", False, None), ("No. Have a good evening.", "Нет. Хорошего вечера.", "you", True, None), ("You too.", "И тебе.", "them", False, None)], S(("Open items before I leave?", "Открытые задачи перед уходом?"), ("Follow up with the vendor.", "Дожми вендора.") ),),
    ],
)


def lines_hash(lines: list[dict]) -> str:
    return hashlib.md5(json.dumps(lines, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def apply_scripts(pack: dict, catalog: dict[str, list], track: str) -> None:
    by_id = {L["id"]: L for L in pack["lessons"]}
    for sec in pack["sections"]:
        sid = sec["id"]
        scripts = catalog.get(sid)
        if not scripts:
            raise SystemExit(f"missing scripts for {track}/{sid}")
        # Numbered stub lessons: `{track}-{sec_id}-01` … `-12` (skip cmds / specials).
        prefix = f"{track}-{sid}-"
        numbered = [
            lid
            for lid in sec["lesson_ids"]
            if lid.startswith(prefix)
            and lid[len(prefix) :].isdigit()
            and len(lid[len(prefix) :]) == 2
        ]
        numbered = sorted(numbered, key=lambda x: int(x.rsplit("-", 1)[-1]))
        if len(numbered) != 12:
            raise SystemExit(f"{track}/{sid}: expected 12 numbered lessons, got {len(numbered)} {numbered}")
        if len(scripts) != 12:
            raise SystemExit(f"{track}/{sid}: expected 12 scripts, got {len(scripts)}")
        for lid, (scene, lines, say) in zip(numbered, scripts):
            lesson = by_id[lid]
            lesson["scene_ru"] = scene
            lesson["lines"] = lines
            lesson["say_today"] = say
            # keep titles/ids/tags/roles/order


def verify_pack(pack: dict, track: str) -> None:
    by_id = {L["id"]: L for L in pack["lessons"]}
    for sec in pack["sections"]:
        hashes = []
        for lid in sec["lesson_ids"]:
            if not lid.rsplit("-", 1)[-1].isdigit():
                continue
            h = lines_hash(by_id[lid]["lines"])
            hashes.append(h)
        uniq = len(set(hashes))
        print(f"  {track}/{sec['id']}: {uniq}/{len(hashes)} unique dialogues")
        if uniq != len(hashes):
            raise SystemExit(f"NON-UNIQUE in {track}/{sec['id']}")


def sync_phrasals_bank() -> None:
    """Merge high-freq essentials from regular CEFR into phrasals_bank (keep existing)."""
    bank_path = ROOT / "phrasals_bank_v1.json"
    reg = json.loads((ROOT / "regular_cefr_pack_v1.json").read_text())
    bank = json.loads(bank_path.read_text())
    existing = {p["en"].lower(): p for p in bank["phrasals"]}
    essentials_roots = {"come", "look", "turn", "get", "take", "put"}
    added = []
    for item in reg["items"]:
        if item.get("kind") != "phrasal":
            continue
        en = item["en"]
        root = en.lower().split()[0]
        if root not in essentials_roots:
            continue
        key = en.lower()
        if key in existing:
            # upgrade empty/generic examples when regular has better
            ex = item.get("example_en") or ""
            if ex and (
                not existing[key].get("example_en")
                or "cable tray" in (existing[key].get("example_en") or "").lower()
            ):
                existing[key]["example_en"] = ex
                if item.get("ru"):
                    existing[key]["ru"] = item["ru"]
            continue
        entry = {
            "en": en,
            "ru": item.get("ru") or "",
            "example_en": item.get("example_en") or f"Can you {en}?",
        }
        existing[key] = entry
        added.append(en)
    bank["phrasals"] = sorted(existing.values(), key=lambda x: x["en"].lower())
    bank_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
    print(f"phrasals_bank: now {len(bank['phrasals'])} (added {added})")
    for r in sorted(essentials_roots):
        ens = [p["en"] for p in bank["phrasals"] if p["en"].lower().split()[0] == r]
        print(f"  bank {r} ({len(ens)}): {ens}")


def main() -> None:
    onsite = json.loads((ROOT / "lessons_onsite_sections_v1.json").read_text())
    regular = json.loads((ROOT / "lessons_regular_sections_v1.json").read_text())
    apply_scripts(onsite, ONSITE, "onsite")
    apply_scripts(regular, REGULAR, "regular")
    print("Verify uniqueness:")
    verify_pack(onsite, "onsite")
    verify_pack(regular, "regular")
    (ROOT / "lessons_onsite_sections_v1.json").write_text(
        json.dumps(onsite, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "lessons_regular_sections_v1.json").write_text(
        json.dumps(regular, ensure_ascii=False, indent=2) + "\n"
    )
    sync_phrasals_bank()
    print("OK wrote packs")


if __name__ == "__main__":
    main()
