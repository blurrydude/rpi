import { Component, Output } from '@angular/core';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() status: object = {};
    constructor(private httpMessageService: StatusService) { 
      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
      });
    }
    
}
