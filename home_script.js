


// To comment out a line in JavaScript, use two forward slashes:
// This is a single-line comment.

// For multiple lines, use /* ... */
/*
This is a
multi-line comment.
*/

// changes the theme of the website 



const doc_html = document.querySelector("html")
const theme_switch = document.querySelector("#theme_switch")


// respect user's preference and change the theme at the beginning
if (localStorage.getItem("theme") === "light")
{
    doc_html.classList.remove("darkmode");
}

function enable_darkmode()
{
    localStorage.setItem('theme', 'dark');
    doc_html.classList.add("darkmode");
    theme_switch.innerHTML


}
function disable_darkmode()
{
    localStorage.setItem('theme', 'light');
    doc_html.classList.remove("darkmode");

}

// listen for clicks and change the theme 
theme_switch.addEventListener("click", () => {

    localStorage.getItem("theme") === "dark" ? disable_darkmode() : enable_darkmode();

    
})

