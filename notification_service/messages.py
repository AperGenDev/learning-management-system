
def build_notification(event: dict) -> dict:
    kind = event.get("event", "")
    data = event.get("data", {})
    course = data.get("course_title", "")

    if kind == "module.added":
        title = "Новый модуль"
        text = f"В курсе «{course}» появился модуль «{data.get('module_title', '')}»"
    elif kind == "course.updated":
        title = "Курс обновлён"
        changes = ", ".join(data.get("changes", [])) or "данные курса"
        text = f"Курс «{course}» изменён (поля: {changes})"
    elif kind == "course.deleted":
        title = "Курс удалён"
        text = f"Курс «{course}», на который вы были записаны, удалён"
    elif kind == "student.enrolled":
        title = "Новый студент"
        text = f"{data.get('student_name', 'Студент')} записался на ваш курс «{course}»"
    else:
        title = "Уведомление"
        text = f"Событие {kind}"

    return {
        "event": kind,
        "title": title,
        "text": text,
        "course_id": data.get("course_id"),
        "created_at": event.get("occurred_at"),
    }
