from collections import deque #Double-Ended Queue -> Parámetro maxlen

#Gracias el parámetro maxlen, cuando llega el número que le decimos, el deque elimina el primer elemento
#Política FIFO

class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self._history = deque(maxlen=max_turns * 2) #Usamos el x2 porque cada turno = user + assistant

    #Añadimos 2 diccionarios -> User + Assistant
    def add_turn(self, user_message: str, assistant_response: str):
        self._history.append({"role": "user",      "content": user_message})
        self._history.append({"role": "assistant", "content": assistant_response})

    #Transforma la estructura de datos interna (lista de diccionarios) en un bloque de texto legible
    def get_history_as_str(self) -> str:
        if not self._history:
            return "Sin historial previo."
        lines = []
        for msg in self._history:
            prefix = "Usuario" if msg["role"] == "user" else "Asistente"
            lines.append(f"{prefix}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        self._history.clear()