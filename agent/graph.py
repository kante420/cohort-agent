from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

from agent.nodes.intent      import intent_node
from agent.nodes.sql_node    import sql_node
from agent.nodes.action_node import action_node
from agent.nodes.viz_node    import viz_node

#Diccionario que viaja a través de todos los nodos
#Cada nodo lee información (como la pregunta) y escribe información nueva (intent o query_result)
#Al ser TypedDict, nos aseguramos de que todos los nodos hablan el mismo idioma
class AgentState(TypedDict, total=False):
    user_question:        str
    conversation_history: str
    intent:               str
    sql:                  str
    query_result:         Optional[object]
    answer:               str
    chart:                Optional[object]
    error:                Optional[str]

#Reenviamos el trabajo al Nodo SQL (más adelante usaremos Ploty aquí)
def estadistica_node(state: dict) -> dict:
    return sql_node(state)

#Si el LLM detecta que no le preguntas por datos, te responde amablemente
def fuera_scope_node(state: dict) -> dict:
    return {**state, "answer": "Solo puedo ayudarte con consultas sobre los datos de pacientes. ¿Tienes alguna pregunta sobre la cohorte?"}

#Lee el intent y decide que camino debe tomar el grafo
def route(state: dict) -> str:
    return state.get("intent", "sql") #Ejecuta sql solo como plan de emegencia

#Dibujamos el mapa
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    #Registarmos todos los nodos
    graph.add_node("intent",      intent_node)
    graph.add_node("sql",         sql_node)
    graph.add_node("estadistica", estadistica_node)
    graph.add_node("accion",      action_node)
    graph.add_node("fuera_scope", fuera_scope_node)
    graph.add_node("viz",         viz_node) 

    #El nodo de entrada siempre es intent
    #Siempre que el usuario pregunte algo, empieza por clasificar su intención
    graph.set_entry_point("intent")

    #Conecta el nodo de intención con los demás, basándonos en la función route()
    graph.add_conditional_edges(
        "intent",
        route,
        {
            "sql":         "sql",
            "estadistica": "estadistica",
            "accion":      "accion",
            "fuera_scope": "fuera_scope",
        }
    )

    #sql y estadistica pasan por viz antes de terminar
    graph.add_edge("sql",         "viz")
    graph.add_edge("estadistica", "viz")

    #Todos los nodos terminales van a END
    #Una vez que el nodo termine su trabajo, puede devolver la respuesta al usuario
    graph.add_edge("viz",         END)
    graph.add_edge("accion",      END)
    graph.add_edge("fuera_scope", END)

    return graph.compile()

agent = build_graph()