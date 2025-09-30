


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
const sidebar = document.querySelector('#sidebar')


// respect user's preference and change the theme at the beginning
if (localStorage.getItem("theme") === "light")
{
    doc_html.classList.remove("darkmode");
}
else
{
    localStorage.setItem('theme', 'dark');
}

function enable_darkmode()
{

    // Temporarily disable navbar animation
    navbar.style.transition = 'none';
    sidebar.style.transition = 'none';

    localStorage.setItem('theme', 'dark');
    doc_html.classList.add("darkmode");

        requestAnimationFrame(() => {
        navbar.style.transition = 'background-color 0.2s ease, color 0.2s ease';
        sidebar.style.transition = 'transform 0.3s ease-in-out, background-color 0.2s ease, color 0.2s ease';
    });


}
function disable_darkmode()
{

    // Temporarily disable navbar animation
    navbar.style.transition = 'none';
    sidebar.style.transition = 'none';


    localStorage.setItem('theme', 'light');
    doc_html.classList.remove("darkmode");


        requestAnimationFrame(() => {
        navbar.style.transition = 'background-color 0.2s ease, color 0.2s ease';
        sidebar.style.transition = 'transform 0.3s ease-in-out, background-color 0.2s ease, color 0.2s ease';
    });

}

// listen for clicks and change the theme 
theme_switch.addEventListener("click", () => {

    localStorage.getItem("theme") === "dark" ? disable_darkmode() : enable_darkmode();

    
})







