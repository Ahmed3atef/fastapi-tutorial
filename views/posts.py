from core.settings import app, templates
from fastapi import Request, HTTPException, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from db.json import posts

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def root(request: Request) -> HTMLResponse:
    context_dict = {
        "title": "Home",
        "posts": posts
    }
    return templates.TemplateResponse(request, "home.html", context=context_dict)

@app.get("/posts/{id}", include_in_schema=False)
def post_view(request: Request, id: int):
    for post in posts:
        if post.get("id") == id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request,
                "post.html",
                {"post": post, "title": title},
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )