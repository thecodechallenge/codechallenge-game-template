import os

import uvicorn


if __name__ == '__main__':
    uvicorn.run(
        'game.server:app',
        host="0.0.0.0",
        port=int(os.environ.get('PORT', 50055)),
        reload=True,
        workers=2,
    )
