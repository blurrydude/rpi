import { Component, Output } from '@angular/core';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() status: object = {};
    @Output() powerstatus: object = {};
    @Output() pistatus: object = {};
    constructor(private httpMessageService: StatusService) { 
      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
      });
      this.httpMessageService.getPowerStatus().toPromise().then(msg => {
        this.powerstatus = msg;
      });
      this.httpMessageService.getPiStatus().toPromise().then(msg => {
        this.pistatus = msg;
      });
    }
    
}
