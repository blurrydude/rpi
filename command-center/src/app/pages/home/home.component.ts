import { Component, Input, Output } from '@angular/core';
import { StatusService } from "../../services/status.service";

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent {
    @Output() status: object = {};
    @Output() pistatus: object = {};
    @Output() readings: object = {};
    @Output() checkins: object = {};
    @Output() motionsensors: object = {};
    @Output() thsensors: object = {};
    @Output() doors: object = {};
    @Output() rollers: object = {};
    @Output() totalPower: number = 0.0;
    @Output() sysmonlog: any = [];
    @Output() apilog: any = [];
    
    constructor(public httpMessageService: StatusService) { 
      this.load(httpMessageService, true)
    }

    public command(com: string) {
      this.httpMessageService.sendCommand(com).toPromise().then(smsg => {this.load(this.httpMessageService,false)});
    }

    public getLogs() {
      this.httpMessageService.getSysMonLog().toPromise().then(lmsg => {
        this.sysmonlog = lmsg;
      });
    }

    public getApiLogs() {
      this.httpMessageService.getApiLog().toPromise().then(lmsg => {
        this.apilog = lmsg;
      });
    }

    public load(httpMessageService: StatusService, main_loop: boolean) {
      if(main_loop == true) setTimeout(()=>{this.load(httpMessageService, true)},15000);

      this.httpMessageService.getMotionSensors().toPromise().then(hmsg => {
        this.motionsensors = hmsg;
      });
      this.httpMessageService.getReadings().toPromise().then(rmsg => {
        this.readings = rmsg;
      });
      this.httpMessageService.getPassiveReadings().toPromise().then(rmsg => {
        this.thsensors = rmsg;
      });
      this.httpMessageService.getDoors().toPromise().then(dmsg => {
        this.doors = dmsg;
      });
      this.httpMessageService.getRollers().toPromise().then(bmsg => {
        this.rollers = bmsg;
      });

      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
        this.totalPower = 0.0;
        for (const [k, v] of Object.entries(this.status)) {
          this.totalPower += parseFloat(v["power"])
        }
        this.httpMessageService.getPiStatus().toPromise().then(smsg => {
          this.pistatus = smsg;
          for (const [k, v] of Object.entries(this.pistatus)) {
            let s = v["heartbeat"].split('_');
            let d = s[0].split('/');
            let t = s[1];
            let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
            let dt = new Date(ms);
            let n = new Date();
            let c = n.getTime() - ms;
            v["class"] = c > 150000 ? "text-danger" : c < 0 ? "text-info" : "text-success";
            v["heartbeat"] = dt;
          }
          this.httpMessageService.getCheckins().toPromise().then(cmsg => {
            this.checkins = cmsg;
            for (const [k, v] of Object.entries(this.checkins)) {
              for (const [sk, sv] of Object.entries(this.status)) {
                if(k != sk) continue;
                if(v.indexOf("NONCOMM") > -1) {
                  sv["checkin"] = "fas fa-tired"
                  continue;
                }
                let s = v.split(', ');
                let d = s[0].split('/');
                let t = s[1];
                let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
                let dt = new Date(ms);
                let n = new Date();
                let c = n.getTime() - ms;
                sv["checkin"] = c > 150000 ? "fas fa-dizzy" : c < 0 ? "far fa-question-circle" : "fas fa-signal";
                sv["heartbeat"] = dt;
              }
            }
          });
        });
      });
    }
    
}
