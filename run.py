import os
from dotenv import load_dotenv
import sys
import uvicorn

if __name__ == '__main__':
    load_dotenv()   

    allowed_args = ["poller", "api"]

    if len(sys.argv) < 2: arg = ''
    else: arg = sys.argv[1]

    if arg == "poller":
        from main.poller import start_polling
        start_polling()

    elif arg == "api":
        uvicorn.run("main.api:app", host="0.0.0.0", port=8000)

    else:
        print(f"Provide one of {allowed_args} as the argument")