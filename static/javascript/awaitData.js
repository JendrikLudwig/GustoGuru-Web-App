function main(){  
    if(document.getElementById("loader") != null) {
        checkData(window.location.href.split("/p/")[1]) 
    }
};

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function checkData(id) {

    let data = null
    do {
        const res = await fetch("/d/"+id)
        const json = await res.json()
        data = JSON.parse(json[1])
        await timeout(3000)

    } while (Object.keys(data.anleitung).length == 0);
    
    location.reload()
    
}