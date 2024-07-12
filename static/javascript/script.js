let selected_tags = []
const USER_STORAGE_ITEM = "user_id"
const USER_RECIPE_ITEM = "user_recipes"

let userId = null
let owned_recipes = null
let toggleBtn = false

// Setup Event Listener on page load
function setupPage() {
    inputField = document.getElementById('searchInput')
    inputField.addEventListener('input', function() {
        const query = this.value;
        fetchSuggestions(query);
    });

    
    // Focus event
    inputField.addEventListener('focus', function() {
        document.getElementsByClassName("search-container")[0].classList.add("active")
    });


    // Blur event
    inputField.addEventListener('blur', function() {
        document.getElementsByClassName("search-container")[0].classList.remove("active")
        
        const activeElement = document.activeElement;
        let sg_active = false
        document.getElementsByClassName("suggestion").forEach(sg => {
            if(sg == activeElement) {
               sg_active = true 
            }
        })

        if(!sg_active) clearSuggestions()
    });

    const toggler = document.getElementById("toggler")
    const toggler_text = document.getElementById("llama_switch_container")

    const tgl_con = document.getElementById("toggle_container")


    document.getElementById("toggle_container").addEventListener("click", x =>  {
        if(toggleBtn) {
            toggler.classList.add("tgl_inactive")
            toggler.classList.remove("tgl_active")
            tgl_con.classList.remove("con_active")
            toggler_text.classList.remove("tgl_text_active")
            toggler_text.classList.add("tgl_text_inactive")
            for (let node of toggler_text.childNodes) {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.nodeValue = 'Llama3 inaktiv';
                    break;
                }
            }



        } else {
            toggler.classList.add("tgl_active")
            toggler.classList.remove("tgl_inactive")
            tgl_con.classList.add("con_active")
            toggler_text.classList.add("tgl_text_active")
            toggler_text.classList.remove("tgl_text_inactive")
            for (let node of toggler_text.childNodes) {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.nodeValue = 'Llama3 aktiv';
                    break;
                }
            }

        }
        toggleBtn = !toggleBtn
    })

    // UUID zuweisung
    userId = window.localStorage.getItem(USER_STORAGE_ITEM)
    
    if(!userId) {
        const res = fetch("/newuser", {
            method: "POST"
        }).then(res => res.json()).then(x => {
            window.localStorage.setItem(USER_STORAGE_ITEM, x.uuid)
            userId = window.localStorage.getItem(USER_STORAGE_ITEM)
            
        })
    }


    // Aside Laden.
    owned_recipes = window.localStorage.getItem(USER_RECIPE_ITEM)
    if(!owned_recipes) {
        window.localStorage.setItem(USER_RECIPE_ITEM, "")
        owned_recipes = window.localStorage.getItem(USER_RECIPE_ITEM)
    }
    updateHistory()
}

// Setup Event Listener on page load
async function setupRecipePage() {
    // UUID zuweisung
    userId = window.localStorage.getItem(USER_STORAGE_ITEM)
    
    if(!userId) {
        const res = fetch("/newuser", {
            method: "POST"
        }).then(res => res.json()).then(x => {
            window.localStorage.setItem(USER_STORAGE_ITEM, x.uuid)
            userId = window.localStorage.getItem(USER_STORAGE_ITEM)
            
        })
    }

    // Aside Laden.
    owned_recipes = window.localStorage.getItem(USER_RECIPE_ITEM)
    if(!owned_recipes) {
        window.localStorage.setItem(USER_RECIPE_ITEM, "")
        owned_recipes = window.localStorage.getItem(USER_RECIPE_ITEM)
    }
    await updateHistory()
    const id = window.location.href.split("/p/")[1]
    const history_tags = document.getElementsByClassName("history_p")
    for (let t of history_tags) {
        console.log(t.getAttribute("id"), id);
        if (t.getAttribute( 'id' ) == id) t.classList.add("active")
    }
}

async function fetchSuggestions(query) {
    const suggestions = await exampleFetchSuggestions(query);
    displaySuggestions(suggestions);
}

async function exampleFetchSuggestions(query) {
    const res = await fetch("/rec/"+query)
    const data = await res.json()
    return data.words
}

function displaySuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    suggestionsContainer.innerHTML = '';
    suggestions.forEach(suggestion => {
        const suggestionElement = document.createElement('div');
        suggestionElement.classList.add('suggestion');
        suggestionElement.textContent = suggestion;
        suggestionElement.addEventListener('click', function() {
            selected_tags.push(suggestion)
            document.getElementById('searchInput').value = "";
            displayTags()
            clearSuggestions();
        });
        if (!selected_tags.includes(suggestion)) {
            suggestionsContainer.appendChild(suggestionElement);
        }
        
    });
}

function clearSuggestions() {
    document.getElementById('suggestionsContainer').innerHTML = '';
}

// Tag Selection
function displayTags() {
    console.log(selected_tags);
    const tagContainer = document.getElementById("tag_container")
    const html = selected_tags.map((tag, idx) => {
        return `<div class='tag' id='tag_${idx}'>${tag}<button class="remove_tag" onclick='removeTag(${idx})'></button></div>`
    })
    console.log(html);
    tagContainer.innerHTML = html.join("")
    
}

function removeTag(id) {
    selected_tags.splice(id, 1)
    displayTags()
}

// Rezept generieren
async function generateRecipe() {
    // Eingabe deaktivieren
    const res = await fetch("/generate",{
        method: "POST",
        headers: {
            'Content-Type': 'application/json'  // Content-Type für JSON-Daten
        },
        body: JSON.stringify({
            llama3: toggleBtn,
            ing:selected_tags
        })

    })
    const data = await res.json()
    console.log(data); 
    addToHistory(data.uuid)
    window.location.href = `/p/${data.uuid}`
}

function addToHistory(uuid) {
    const uuids = window.localStorage.getItem(USER_RECIPE_ITEM)
    let uuid_arr = null
    if (uuids.length == 0) uuid_arr = []
    else uuid_arr = uuids.split(",")
    uuid_arr.push(uuid)
    window.localStorage.setItem(USER_RECIPE_ITEM, uuid_arr.join(","))  
}

async function updateHistory() {
    const dom = document.getElementById("history_entries")
    const uuids = window.localStorage.getItem(USER_RECIPE_ITEM)
    let uuid_arr = null
    let html = null
    if (uuids.length == 0) {
        html = ["<div class='no_history'>Keine Rezepte gefunden.</div>"]
    } 
    else {
        uuid_arr = uuids.split(",")
        html =  await Promise.all(uuid_arr.map(async id =>{
            const res = await fetch("/d/"+id)
            const json = await res.json()
            const zutaten = JSON.parse(json[1]).zutaten.join(", ")

            return `<a href="/p/${id}"><p class="history_p" id="${id}">${zutaten}</p></a>`
        }))
    } 
    dom.innerHTML = html.reverse().join("")
 
}
