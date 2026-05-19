/* ================= SIDEBAR ================= */

function toggleSidebar() {

    const sidebar =
        document.getElementById("sidebar");

    const main =
        document.querySelector(".main");

    if (window.innerWidth <= 768) {

        sidebar.classList.toggle("show-sidebar");

    } else {

        sidebar.classList.toggle("collapsed");

        main.classList.toggle("expanded");
    }
}


/* ================= SWITCH VIEWS ================= */

function switchView(view, element = null) {

    const sidebar =
        document.getElementById("sidebar");

    const main =
        document.querySelector(".main");

    /* OPEN SIDEBAR AGAIN IF COLLAPSED */

    if (sidebar.classList.contains("collapsed")) {

        sidebar.classList.remove("collapsed");

        main.classList.remove("expanded");
    }

    /* SWITCH VIEWS */

    document.querySelectorAll(".view")
        .forEach(v => {
            v.classList.remove("active-view");
        });
/* REFRESH WHEN SWITCHING VIEWS */

if (

    view === "dashboard"

    &&

    !document
        .getElementById(
            "dashboardView"
        )
        .classList.contains(
            "active-view"
        )

) {

    location.reload()

    return
}
    const target =
        document.getElementById(view + "View");

    if (target) {

        target.classList.add("active-view");
    }

    /* ACTIVE MENU */

    document.querySelectorAll(".menu-item")
        .forEach(item => {
            item.classList.remove("active");
        });

    if (element) {

        element.classList.add("active");
    }
}


/* ================= OPEN MODAL ================= */

function openUpload() {

    document.getElementById("uploadModal")
        .classList.add("show");
}


/* ================= CLOSE MODAL ================= */

function closeUpload() {

    document.getElementById("uploadModal")
        .classList.remove("show");
}


/* ================= FILE PREVIEW ================= */

document.addEventListener("DOMContentLoaded", () => {

    const fileInput =
        document.getElementById("fileInput");

    if (fileInput) {

        fileInput.addEventListener("change", function () {

            const files = [...this.files];

            const preview =
                files.map(file => file.name)
                    .join(", ");

            document.getElementById("filePreview")
                .innerText = preview;

        });

    }

});


/* ================= FILTER FILES ================= */

function filterFiles(type, element) {

    document.querySelectorAll(".category")
        .forEach(cat => {
            cat.classList.remove("active-category");
        });

    if (element) {

        element.classList.add("active-category");
    }

    const files =
        document.querySelectorAll(".file-item");

    files.forEach(file => {

        const fileType =
            file.dataset.type;

        if (type === "all") {

            file.style.display = "grid";
        }

        else if (fileType === type) {

            file.style.display = "grid";
        }

        else {

            file.style.display = "none";
        }

    });

}


/* ================= SORT FILES ================= */

function sortFiles(value) {

    const tables =
        document.querySelectorAll(".file-table");

    tables.forEach(table => {

        const rows =
            [...table.querySelectorAll(".file-item")];

        rows.sort((a, b) => {

            if (value === "name") {

                return a.dataset.name
                    .localeCompare(b.dataset.name);
            }

            if (value === "date") {

                return b.dataset.timestamp -
                    a.dataset.timestamp;
            }

        });

        rows.forEach(row => {
            table.appendChild(row);
        });

    });

}


/* ================= SEARCH FILES ================= */

function searchFiles() {

    const input =
        document.getElementById("searchInput");

    const filter =
        input.value.toLowerCase();

    const files =
        document.querySelectorAll(".file-item");

    files.forEach(file => {

        const fileName =
            file.dataset.name.toLowerCase();

        if (fileName.includes(filter)) {

            file.style.display = "grid";
        }

        else {

            file.style.display = "none";
        }

    });

}





/* ================= DRAG & DROP ================= */

const uploadArea =
    document.getElementById("uploadArea");

if (uploadArea) {

    uploadArea.addEventListener("dragover", (e) => {

        e.preventDefault();

        uploadArea.style.borderColor =
            "#4f46e5";

    });

    uploadArea.addEventListener("dragleave", () => {

        uploadArea.style.borderColor =
            "#d1d5db";

    });

    uploadArea.addEventListener("drop", (e) => {

        e.preventDefault();

        const files =
            e.dataTransfer.files;

        const fileInput =
            document.getElementById("fileInput");

        fileInput.files = files;

        const preview =
            [...files]
                .map(file => file.name)
                .join(", ");

        document.getElementById("filePreview")
            .innerText = preview;

    });

}


/* ================= ICONS ================= */

lucide.createIcons();
/* ================= AUTO REMOVE TOAST ================= */

setTimeout(() => {

    const toasts =
        document.querySelectorAll(".toast");

    toasts.forEach(toast => {

        toast.style.opacity = "0";

        toast.style.transform =
            "translateX(50px)";

        setTimeout(() => {

            toast.remove();

        }, 400);

    });

}, 3000);
/* ================= VIEW MORE ================= */

let expanded = false;

function toggleViewMore() {

    const extraFiles =
        document.querySelectorAll(".extra-file");

    const text =
        document.getElementById("viewMoreText");

    expanded = !expanded;

    extraFiles.forEach((file, index) => {

        if (index >= 6) {

            if (expanded) {

                file.style.display = "";

            }

            else {

                file.style.display = "none";
            }
        }

    });

    text.innerText =
        expanded
            ? "Show Less"
            : "View More";
}
/* ================= UPLOAD PROGRESS ================= */

const uploadForm =
    document.querySelector("form");

if (uploadForm) {

    uploadForm.addEventListener("submit", () => {

        const fill =
            document.getElementById(
                "uploadProgressFill"
            );

        const text =
            document.getElementById(
                "uploadProgressText"
            );

        let progress = 0;

        const interval =
            setInterval(() => {

                progress += 10;

                fill.style.width =
                    progress + "%";

                text.innerText =
                    "Uploading... " +
                    progress + "%";

                if (progress >= 100) {

                    clearInterval(interval);

                    text.innerText =
                        "Upload Complete";
                }

            }, 120);

    });

}
/* ================= REMOVE EMPTY STATE ================= */

function removeEmptyState(containerId) {

    const container =

        document.getElementById(
            containerId
        )

    if (!container) return

    const emptyState =

        container.querySelector(
            ".empty-state"
        )

    if (emptyState) {

        emptyState.remove()
    }
}

/* ================= FAVORITES ================= */

async function toggleFavorite(
    filename,
    element
) {

    try {

        const response = await fetch(

            "/favorite/" + filename,

            {
                method: "GET"
            }
        )

        if (response.ok) {

            const isFavorited =

                element.classList.contains(
                    "favorite-btn"
                )

                    ?

                    element.classList.contains(
                        "favorited"
                    )

                    :

                    true

            localStorage.setItem(

                "toastMessage",

                isFavorited

                    ?

                    "Removed from favorites"

                    :

                    "Added to favorites"
            )

            element.classList.toggle(
                "favorited"
            )

            showToast(

                isFavorited

                    ?

                    "Removed from favorites"

                    :

                    "Added to favorites"
            )

            refreshFavorites()
        }

    }

    catch (error) {

        console.log(

            "Favorite error:",

            error
        )
    }
}
/* ================= SHOW TOAST ================= */

function showToast(message, type = "success") {

    let container =
        document.querySelector(
            ".toast-container"
        );


    /* CREATE IF MISSING */

    if (!container) {

        container =
            document.createElement("div");

        container.className =
            "toast-container";

        document.body.appendChild(
            container
        );
    }

    const toast =
        document.createElement("div");

    toast.className =
        "toast toast-" + type;

    toast.innerHTML =
        `<span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {

        toast.style.opacity = "0";

        toast.style.transform =
            "translateX(50px)";

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, 2500);

}
/* ================= SHARE FILE ================= */

async function shareFile(filename) {

    try {

        const response = await fetch(

            "/share/" + filename
        )

        const data =
            await response.json()

        await navigator.clipboard.writeText(

            data.url
        )

        showToast(

            "Share link copied!"
        )
    }

    catch(error) {

        console.log(

            "Share error:",

            error
        )

        showToast(

            "Failed to create share link",

            "delete"
        )
    }
}
/* ================= RELOAD TOAST ================= */

window.addEventListener("load", () => {

    const message =
        localStorage.getItem(
            "toastMessage"
        );

    if (message) {

        showToast(message);

        localStorage.removeItem(
            "toastMessage"
        );
    }

});
/* ================= FILE PREVIEW ================= */

async function previewFile(

    filename,

    source = "uploads"

){

    const modal =
        document.getElementById(
            "previewModal"
        )

    const content =
        document.getElementById(
            "previewContent"
        )

    const extension =
        filename
            .split(".")
            .pop()
            .toLowerCase()

    try {

        const response = await fetch(

            `/file-url/${filename}?source=${source}`
        )

        const data =
            await response.json()

        const fileUrl =
            data.url

        /* PDF */

        if (extension === "pdf") {

            content.innerHTML = `

                <iframe
                    src="${fileUrl}"
                    allow="autoplay"
                    style="
                        width:100%;
                        height:100%;
                        border:none;
                    "
                ></iframe>

            `
        }

        /* IMAGES */

        else if (

            extension === "png" ||
            extension === "jpg" ||
            extension === "jpeg" ||
            extension === "gif" ||
            extension === "webp"

        ) {

            content.innerHTML = `

                <img
                    src="${fileUrl}"
                    style="
                        max-width:100%;
                        max-height:100%;
                        object-fit:contain;
                    "
                >

            `
        }

        /* UNSUPPORTED */

        else {

            content.innerHTML = `

                <div
                    style="
                        height:100%;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:22px;
                        color:#6b7280;
                    "
                >

                    Preview not supported

                </div>

            `
        }

        modal.classList.add("show")
    }

    catch(error) {

        console.log(
            "Preview error:",
            error
        )
    }
}
/* CLOSE */

function closePreview() {

    document.getElementById(
        "previewModal"
    ).classList.remove("show");

}
/* ================= DRAG & DROP ================= */

const dropZone =
    document.getElementById(
        "dropZone"
    );

const fileInput =
    document.getElementById(
        "fileInput"
    );

if (dropZone && fileInput) {

    /* DRAG OVER */

    dropZone.addEventListener(

        "dragover",

        (e) => {

            e.preventDefault();

            dropZone.classList.add(
                "dragover"
            );

        }

    );

    /* DRAG LEAVE */

    dropZone.addEventListener(

        "dragleave",

        () => {

            dropZone.classList.remove(
                "dragover"
            );

        }

    );

    /* DROP */

    dropZone.addEventListener(

        "drop",

        (e) => {

            e.preventDefault();

            dropZone.classList.remove(
                "dragover"
            );

            fileInput.files =
                e.dataTransfer.files;

        }

    );

}
/* ================= SKELETON LOADING ================= */

window.addEventListener("load", () => {

    const skeleton =
        document.getElementById(
            "skeletonScreen"
        );

    const realContent =
        document.getElementById(
            "realContent"
        );

    setTimeout(() => {

        skeleton.style.display =
            "none";

        realContent.style.display =
            "block";

    }, 900);

});
function openProfileModal() {

    document
        .getElementById(
            'profileModal'
        )
        .classList.add('show')
}


function closeProfileModal() {

    document
        .getElementById(
            'profileModal'
        )
        .classList.remove('show')
}


document
    .getElementById(
        'profileModal'
    )
    .addEventListener(
        'click',
        function(e) {

            if (e.target === this) {

                closeProfileModal()
            }
        }
    )
    async function toggleDarkMode() {

        document.body.classList.toggle(
            "dark-mode"
        )
    
        const isDark =
    
            document.body.classList.contains(
                "dark-mode"
            )
    
        try {
    
            await fetch(
    
                "/toggle-theme",
    
                {
    
                    method: "POST",
    
                    headers: {
    
                        "Content-Type":
                        "application/json"
                    },
    
                    body: JSON.stringify({
    
                        theme:
                        isDark
                            ? "dark"
                            : "light"
                    })
                }
            )
    
        }
    
        catch(error) {
    
            console.log(
                "Theme error:",
                error
            )
        }
    }
/* ================= DELETE FILE ================= */

async function deleteFile(
    filename,
    element
) {

    try {

        const response = await fetch(

            "/delete/" + filename,

            {
                method: "GET"
            }
        )

        if (response.ok) {

            showToast(
                "File moved to trash"
            )

            setTimeout(() => {

                location.reload()

            }, 200)
        }

    }

    catch(error) {

        console.log(

            "Delete error:",

            error
        )
    }
}


/* ================= RECOVER FILE ================= */

async function recoverFile(
    filename,
    element
) {

    try {

        const response = await fetch(

            "/recover/" + filename,

            {
                method: "GET"
            }
        )

        if (response.ok) {

            showToast(
                "File recovered"
            )

            setTimeout(() => {

                location.reload()

            }, 200)
        }

    }

    catch(error) {

        console.log(

            "Recover error:",

            error
        )
    }
}


/* ================= PERMANENT DELETE ================= */

async function permanentDeleteFile(
    filename,
    element
) {

    try {

        const response = await fetch(

            "/permanent-delete/" + filename,

            {
                method: "GET"
            }
        )

        if (response.ok) {

            showToast(
                "File deleted forever",
                "delete"
            )

            setTimeout(() => {

                location.reload()

            }, 200)
        }

    }

    catch(error) {

        console.log(

            "Permanent delete error:",

            error
        )
    }
}
/* ================= REFRESH FAVORITES ================= */

async function refreshFavorites() {

    try {

        const response = await fetch(

            "/favorites-partial"
        )

        const html = await response.text()

        document.getElementById(
            "favoritesContainer"
        ).innerHTML = html

        lucide.createIcons()
    }

    catch(error) {

        console.log(

            "Favorites refresh error:",

            error
        )
    }
}
