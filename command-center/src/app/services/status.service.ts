import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
// import { TriageDetailMessage } from '../models/triage-detail-message';
// import { LoanCalculationMessage } from '../models/loan-calculation-message';
// import { LoanMessage } from '../models/loan-message';

@Injectable({
  providedIn: 'root'
})
export class StatusService {
  public auth: string = '';
  public user: string = '';
  private baseurl: string;
  // private byCompanyUrl: string;
  // private triageDetailUrl: string;
  // private loanCalculationUrl: string;
  // private byIdUrl: string;
  // private fileUrl: string;
  private options: {
    headers: HttpHeaders
    params: HttpParams
  };

  constructor(private http: HttpClient) {
    this.baseurl = "https://api.idkline.com/"
    // this.baseurl = "http://localhost:8080/"
    // this.baseurl = environment.loansRequestService;
    // this.byCompanyUrl = environment.loansInformationByCompany;
    // this.byIdUrl = environment.loansInformationById;
    // this.triageDetailUrl = environment.triageDetailByCompany;
    // this.loanCalculationUrl = environment.loanCalculation;
    // this.fileUrl = environment.fileUpload;

    let httpHeaders = new HttpHeaders()
      // httpHeaders.set('client_id', environment.wfsMulesoftClientId);
      // httpHeaders.set('client_secret', environment.wfsMulesoftClientSecret);

    this.options = { headers: httpHeaders, params: new HttpParams() };
  }

  public getStatus() {
    return this.http.get(this.baseurl+"webstates", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getPiStatus() {
    return this.http.get(this.baseurl+"pistates", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getPassiveReadings() {
    return this.http.get(this.baseurl+"getpassivereadings", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getReadings() {
    return this.http.get(this.baseurl+"getreadings", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getTemplog() {
    return this.http.get(this.baseurl+"gettemplog", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getPowerlog() {
    return this.http.get(this.baseurl+"getpowerlog", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getDoors() {
    return this.http.get(this.baseurl+"getdoors", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getMode() {
    return this.http.get(this.baseurl+"getmode", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getRollers() {
    return this.http.get(this.baseurl+"getrollers", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getMotionSensors() {
    return this.http.get(this.baseurl+"getmotionsensors", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getCheckins() {
    return this.http.get(this.baseurl+"checkins", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getShellies() {
    return this.http.get(this.baseurl+"getshellies", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getSysMonLog() {
    return this.http.get(this.baseurl+"getsysmonlog", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getApiLog() {
    return this.http.get(this.baseurl+"getapilog", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getToken(username: string, passhash: string) {
    return this.http.post(this.baseurl+"gettoken", {"username":username, "passhash":passhash},this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public sendCommand(command: string) {
    let httpHeaders = new HttpHeaders({
      "user":this.user,
      "auth":this.auth
    });

    let opts = { headers: httpHeaders, params: new HttpParams() };
    console.log(opts)
    return this.http.get(this.baseurl+"webcontrol/"+command, opts)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public sendThermosettings(room: string, temp_low: number, temp_high: number, humidity: number, circ_min: number, hum_circ_min: number, stage_limit: number, stage_cooldown: number) {
    let httpHeaders = new HttpHeaders({
      "user":this.user,
      "auth":this.auth
    });

    let opts = { headers: httpHeaders, params: new HttpParams() };
    console.log(opts)
    return this.http.get(this.baseurl+"webthermoset/"+room+"-"+temp_low+"-"+temp_high+"-"+humidity+"-"+circ_min+"-"+hum_circ_min+"-"+stage_limit+"-"+stage_cooldown, opts)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 0) {
      // A client-side or network error occurred.
      console.error('An error occurred:', error.error);
    } else {
      // The backend returned an unsuccessful response code.
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was:`,error);
    }
    // Return an observable with a user-facing error message.
    return throwError(
      'Something bad happened; please try again later.');
  }
}