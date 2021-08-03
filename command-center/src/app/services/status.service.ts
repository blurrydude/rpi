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
    // this.baseurl = "https://api.idkline.com/"
    this.baseurl = "http://localhost:8080/"
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

  public getReadings() {
    return this.http.get(this.baseurl+"getreadings", this.options)
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

  public getToken(username: string, passhash: string) {
    return this.http.post(this.baseurl+"gettoken", {"username":username, "passhash":passhash},this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public sendCommand(command: string) {
    let httpHeaders = new HttpHeaders()
    httpHeaders.set('client_id', environment.wfsMulesoftClientId);
    httpHeaders.set('client_secret', environment.wfsMulesoftClientSecret);

    let opts = { headers: httpHeaders, params: new HttpParams() };
    return this.http.get(this.baseurl+"getdoors", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  // public getLoansByCompany(companyNumber: string) {
  //   this.options.params = new HttpParams({ fromString: "?companyId=" + companyNumber });
  //   return this.http.get<LoanMessage[]>(this.byCompanyUrl, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     );
  // }

  // public getTriageDetailsByCompany(companyNumber: string) {
  //   this.options.params = new HttpParams({ fromString: "?companyId=" + companyNumber });
  //   return this.http.get<TriageDetailMessage[]>(this.triageDetailUrl, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     );
  // }

  // public getLoanCalculationByCompany(companyNumber: string, term: number, triageScore: number) {
  //   this.options.params = new HttpParams({ fromString: "?companyId=" + companyNumber + "&term=" + term + "&triageScore=" + triageScore });
  //   return this.http.get<LoanCalculationMessage>(this.loanCalculationUrl, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     );
  // }

  // public getLoansById(id: string) {
  //   this.options.params = new HttpParams({ fromString: "?requestId=" + id });
  //   return this.http.get<LoanMessage>(this.byIdUrl, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     );
  // }

  // public createLoansRequest(message: LoanMessage) {//todo might need to update once backend is updated?
  //   return this.http.post<string>(this.baseurl, message, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     )
  // }

  // public editLoansRequest(message: string): Observable<any> {
  //   this.options.headers.set('Accept', '*/*');
  //   return this.http.put<string>(this.baseurl, message, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     )
  // }

  // public deleteLoansRequest(id: string): Observable<any> {
  //   return this.http.delete<string>(this.baseurl + '?requestId=' + id, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     ) 
  // }

  // public postFile(fileToUpload: File) {
  //   const formData: FormData = new FormData();
  //   formData.append('file', fileToUpload, fileToUpload.name);
  //   this.options.headers.append("Content-Type", "multipart/form-data")
  //   return this.http.post(this.fileUrl, formData, this.options)
  //     .pipe(
  //       catchError(err => {
  //         return this.handleError(err);
  //       })
  //     )
  // }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 0) {
      // A client-side or network error occurred.
      console.error('An error occurred:', error.error);
    } else {
      // The backend returned an unsuccessful response code.
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was: ${error.error}`);
    }
    // Return an observable with a user-facing error message.
    return throwError(
      'Something bad happened; please try again later.');
  }
}