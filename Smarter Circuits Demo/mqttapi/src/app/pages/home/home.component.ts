import { Component, Input, Output } from "@angular/core";
import { ApiService } from "src/app/services/api.service";

@Component({
    selector: 'home',
    templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() states: object = {};

    constructor(public apiService: ApiService) {
        this.getStates();
    }

    public getStates() {
        console.log("get states");
        this.apiService.getStates().toPromise().then(msg => {
            this.states = msg;
            console.log(this.states);
        });
    }

    public toggle(circuit: string, current_state: string) {
        let state = current_state == "on" ? "off" : "on";
        console.log("toggle "+circuit+" "+state);
        this.apiService.sendCommand(circuit.replace("_"," ")+" "+state).toPromise().then(msg => {
            console.log(msg);
           setTimeout(()=>{this.getStates()},2000);
        });
    }
}