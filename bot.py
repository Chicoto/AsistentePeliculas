from movies import search, search_platforms
from openai import OpenAI
from models import User
from langsmith import traceable


def build_prompt(user: User, context: str):
    system_prompt = '''Eres un chatbot que recomienda películas, te llamas 'BuscaPelis'.
    - Tu rol es responder recomendaciones de manera breve y concisa.
    - No repitas recomendaciones.
    '''

   

    if context:
        system_prompt += f'Además considera el siguiente contenido: {context}\n'

    return system_prompt


@traceable(run_type="tool", name="where_to_watch")
def where_to_watch(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search_platforms(search_term)
    print("llama a where_to_watch")
    if not movie_or_tv_show:
        return f'No estoy seguro de dónde puedes ver esta película o serie :(, pero quizas puedes revisar en JustWatch: https://www.justwatch.com/cl/buscar?q={search_term}'

    system_prompt = build_prompt(user, str(movie_or_tv_show))

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content


@traceable(run_type="tool", name="search_movie_or_tv_show")
def search_movie_or_tv_show(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search(search_term)
    print("llama a search_movie_or_tv_show")
    if movie_or_tv_show:
        system_prompt = build_prompt(user, str(movie_or_tv_show))
    else:
        system_prompt = build_prompt(user, '')

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content