def breadcrumbs(request):
    path = request.path.strip("/").split("/")  
    home_url = "/organizer/dashboard/" if request.user.is_staff else "/dashboard/"  # Set home URL dynamically

    breadcrumbs = [{"name": "Home", "url": home_url}]  # Always start with Home
    
    ignored_pages = ["organizer"]  # Add any other pages to ignore

    if path and path[0]:  
        url = ""
        for segment in path:
            if segment in ignored_pages:
                continue  # Skip ignored pages
            
            url += f"/{segment}"
            breadcrumbs.append({"name": segment.replace("-", " ").title(), "url": url})

    return {"breadcrumbs": breadcrumbs}
