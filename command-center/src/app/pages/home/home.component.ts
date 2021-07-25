import { Component } from '@angular/core';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    //thing: object;
    constructor(private httpMessageService: StatusService) { 
      this.httpMessageService.getStatus().toPromise().then(msg => {
        console.log(msg);
      });
    }
    
}
