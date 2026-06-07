function refreshPage() {
  window.location.reload();
}

function routeToPath(path) {
    if (path) {
        console.log("Routing to: ", path);
        window.open(path, "_self");
    }
}
