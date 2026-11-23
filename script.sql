use bd2025;
-- select cliente ,funcionario, produto
-- insert itemvenda,venda,  
-- update produto, em saldo
select * from venda;
select * from filial;

select clicodigo as id,clinome as nome from cliente;
select procodigo as id, pronome as nome, prosaldo as qtde from produto;
select funcodigo as id,funnome as nome from funcionario;

delimiter &&
create procedure sp_inserir_venda(idvenda int,anomes varchar(10),filial int,clicodigo int , funcodigo int,fpcodigo int)
begin

	-- verificar se existe: funcionario,cliente,filial e produto

insert into venda()
values (idvenda,anomes,filial,clicodigo,funcodigo,fpcodigo);
end&&
delimiter ;

delimiter &&
create procedure sp_inserir_itemvenda(idvenda int,procodigo int,itvqtde int )
begin
insert into itemvenda()
values (idvenda,procodigo,itvqtde);
end&&
delimiter ;
-- atualiza o saldo do produto
delimiter &&
create procedure sp_updade_produto(codigo int,saldo int)
begin

	declare qtde int;
    
    select prosaldo
    into qtde
    from produto
    where procodigo = codigo;

	if qtde < saldo then
		signal sqlstate '45000'
			set message_text = 'Quantidade do saldo é menor que a quantidade que deseja ser retirada';
    else
		update produto
		set prosaldo = prosaldo - saldo
		where procodigo = codigo;
    end if;
end&&
delimiter ;


delimiter &&
create procedure fazer_venda(
	idvenda int,
	anomes varchar(10),
    filial int,
    clicodigo int , 
    funcodigo int,
    fpcodigo int,
    produto_codigo int,
    itvqtde int
)
begin
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Erro na operação: a transação foi totalmente desfeita (ROLLBACK).' AS status;
    END;    
    start transaction;
    call sp_inserir_venda(idvenda, anomes, filial, clicodigo, funcodigo, fpcodigo);
    call sp_inserir_itemvenda(idvenda, produto_codigo, itvqtde);
    call sp_updade_produto(produto_codigo,itvqtde);
    
    commit;
    select 'Opereção concluida!';
end&&
delimiter ;
drop procedure fazer_venda;
call fazer_venda(114,"2026-11-12",1,10,5,1,1,2);
delete from venda where vencodigo = 114;
delete from itemvenda where itvvencodigo = 114;
select * from venda where vencodigo = 114;
select * from itemvenda where itvvencodigo = 114;
select * from produto ;
ROLLBACK;
SET autocommit = 1;
SELECT * FROM venda WHERE vencodigo= 114;
