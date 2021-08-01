import { Component, Output } from '@angular/core';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() status: object = {};
    @Output() pistatus: object = {};
    @Output() readings: object = {};
    @Output() doors: object = {};
    
    constructor(private httpMessageService: StatusService) { 
      this.load(httpMessageService)
    }

    public load(httpMessageService: StatusService) {
      setTimeout(()=>{this.load(httpMessageService)},5000);
      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
        this.httpMessageService.getPiStatus().toPromise().then(smsg => {
          this.pistatus = smsg;
          this.httpMessageService.getReadings().toPromise().then(rmsg => {
            this.readings = rmsg;
            this.httpMessageService.getDoors().toPromise().then(dmsg => {
              this.doors = dmsg;
            });
          });
        });
      });
    }
    
}
