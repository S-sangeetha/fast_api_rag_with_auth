import { Injectable } from '@angular/core';
import { environment } from '../../../../../environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UploaddocService {
  uploadApiUrl = environment.uploadServiceUrl
  constructor(private http: HttpClient) { }

  upload_doc(formData: FormData) {
    return this.http.post(
      `${this.uploadApiUrl}`,
      formData
    );
  }
}
