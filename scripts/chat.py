from bs4 import BeautifulSoup

from src.ai_agent import dialog_router

if __name__=='__main__':
    human_input = input("User 👤: ")
    for k in range(10):
        answer = dialog_router(human_input=human_input, user={'user_name': 'average_human', 'name': 'Average Human'})
        if answer['final_answer']:
            text = BeautifulSoup(answer['answer'], 'html.parser').get_text()
            print(f"Agent 🤖: {text}")
            break
        else:
            print(f"Agent 🤖: {answer['answer']}")
            human_input = input("User 👤: ")
            print('\n..............\n')
    if k == 6:
        print("Conversation length overflow")