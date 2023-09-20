let dataTable;
let dataTableIsInit = false;

const dataTableOptions = {
    columnDefs:[
        {className:'centered', targets:[0,1,2,3,4]},
        {orderable:false, targets:[3,4]},
        {searchable:false, targets:[4]}
    ],
    pageLength:10,
    destroy:true,
};
const initDataTable=async()=>{
    if(dataTableIsInit){
        dataTable.destroy();
    }
    await listPlays();
    dataTable = $('#plays-table-test').DataTable(dataTableOptions);
    dataTableIsInit = true;
};

const listPlays=async()=>{
    try{
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-plays-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.plays.forEach((play)=>{
            content+=`
                <tr>
                    <td>${play.student_id}</td>
                    <td>${play.game__name}</td>
                    <td>${play.time}</td>
                    <td>${play.ended == true 
                        ? "<i class='fa-solid fa-check' style='color:green;'></i>" 
                        : "<i class='fa-solid fa-xmark' style='color:red;'></i>" }
                    </td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
                        <button class='btn btn-sm btn-danger'><i class='fa-solid fa-trash-can'></i></button>
                    </td>
                </tr>
            `;
        });
        var tableBody_plays = document.getElementById("tableBody_plays");
        tableBody_plays.innerHTML=content;
    }catch(err){
        alert(err);
    }
};

window.addEventListener('load',async()=>{
    await initDataTable();
});