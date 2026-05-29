# PubStar Web - Architecture Rules

Tài liệu này mô tả nhanh cấu trúc và quy ước nhẹ cho dự án `pubstar-web`.
Mục đích: giúp AI và Developer hiểu vị trí code, sửa đúng nơi, không tạo rule quá chặt gây khó phát triển.

## 1. Tổng quan dự án

`pubstar-web` là ứng dụng web dùng Next.js 14, React 18, TypeScript, Ant Design, SCSS và API client sinh từ OpenAPI.

Các khu vực chính:

* `/src/app`: App Router của Next.js, chứa route, layout, page theo locale và theo nhóm màn hình.
* `/src/app/[locale]/(auth)`: Các màn hình đăng nhập, đăng ký, quên mật khẩu, xác thực email.
* `/src/app/[locale]/(home)`: Trang public như landing page, privacy policy, terms.
* `/src/app/[locale]/(protected)`: Các màn hình cần đăng nhập, bao gồm user dashboard và admin.
* `/src/components`: Component dùng lại nhiều nơi, ví dụ form, modal, table, layout, icon, auth component.
* `/src/hooks`: Custom hooks dùng chung cho fetch option, notification, filter, view-as-publisher, v.v.
* `/src/services/openapi`: API client được generate từ `swagger.json`. Hạn chế sửa tay trực tiếp trong thư mục này.
* `/src/utils`: Helper, constant, interface và logic tiện ích dùng chung.
* `/src/navigation`, `/src/i18n.ts`: Điều hướng và cấu hình đa ngôn ngữ.
* `/public/assets`: Ảnh, icon, SVG và static assets.

## 2. Quy tắc làm việc đơn giản

1. **Giữ đúng vị trí code:** Route/page để trong `/src/app`; UI dùng lại để trong `/src/components`; logic dùng lại để trong `/src/hooks` hoặc `/src/utils`.
2. **Không làm rule quá chặt:** Ưu tiên sửa theo pattern đang có trong file/thư mục gần nhất. Không refactor lớn nếu yêu cầu chỉ là bug fix hoặc thay đổi nhỏ.
3. **Client/Server Component:** Chỉ thêm `"use client"` khi component cần hook React, browser API, event handler hoặc state. Không thêm bừa vào page/layout nếu không cần.
4. **API:** Ưu tiên dùng `DefaultApi` và type từ `/src/services/openapi`. Nếu cần đổi API contract, cập nhật `swagger.json` rồi generate lại thay vì sửa trực tiếp file generate.
5. **UI:** Ưu tiên Ant Design và component sẵn có trong `/src/components`. SCSS nên đặt gần màn hình/component đang dùng, theo pattern hiện tại.
6. **Form/Table/Filter:** Khi thêm màn hình CRUD/list, tham khảo các màn hình có sẵn trong admin hoặc user area để giữ UX nhất quán.
7. **i18n:** Với text hiển thị cho user, ưu tiên theo cơ chế translation hiện có nếu màn hình đó đang dùng đa ngôn ngữ. Không bắt buộc refactor toàn bộ text cũ.
8. **Auth & permission:** Không bỏ qua protected layout, view-as-publisher hoặc logic quyền hiện có khi sửa màn hình trong `(protected)`.
9. **TypeScript:** Dùng type rõ ràng cho data quan trọng, nhưng không cần over-engineer generic/phân tầng nếu feature nhỏ.
10. **Trước khi sửa lớn:** Nếu thay đổi ảnh hưởng nhiều route, API client, auth hoặc permission, hãy đọc thêm file liên quan và xác nhận phạm vi trước.

## 3. Nguyên tắc refactor cho AI

* Bảo toàn route, URL, query param và behavior public nếu không được yêu cầu đổi.
* Không đổi cấu trúc response/API usage khi chưa kiểm tra backend hoặc OpenAPI type.
* Không xóa các disable ESLint/comment hiện có nếu chưa hiểu lý do.
* Ưu tiên thay đổi nhỏ, dễ review, đúng mục tiêu.
